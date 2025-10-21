#!/usr/bin/env python3
"""
NCBI MCP Server - Connects to NCBI E-utilities for genomics data retrieval
Part of GenoScope - Universal Genomics Data Platform
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
import aiohttp
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
from dataclasses import dataclass

# MCP Server base classes (simplified for prototype)
class MCPServer:
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.resources = {}
    
    def add_tool(self, name: str, func, description: str):
        self.tools[name] = {"func": func, "description": description}
    
    def add_resource(self, name: str, func, description: str):
        self.resources[name] = {"func": func, "description": description}

@dataclass
class NCBISearchResult:
    id: str
    title: str
    summary: str
    organism: str
    study_type: str
    samples_count: int
    accession: str

class NCBIMCPServer(MCPServer):
    def __init__(self):
        super().__init__("NCBI Genomics Data Server")
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.api_key = os.getenv("NCBI_API_KEY", "")
        self.setup_tools()
    
    def setup_tools(self):
        """Register available tools with the MCP server"""
        self.add_tool(
            "search_genomics_data",
            self.search_genomics_data,
            "Search NCBI databases for genomics datasets by query terms"
        )
        
        self.add_tool(
            "get_study_details",
            self.get_study_details, 
            "Get detailed information about a specific study"
        )
        
        self.add_tool(
            "download_sequences", 
            self.download_sequences,
            "Download DNA/RNA/protein sequences in FASTA format"
        )
        
        self.add_tool(
            "search_geo_datasets",
            self.search_geo_datasets,
            "Search GEO for expression datasets"
        )
    
    async def search_genomics_data(self, query: str, database: str = "nuccore", 
                                 max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search NCBI databases for genomics data
        
        Args:
            query: Search terms (e.g., "BRCA1 human", "COVID-19 RNA-seq")
            database: NCBI database (nuccore, protein, sra, geo)
            max_results: Maximum number of results to return
        """
        try:
            # Step 1: Search for IDs
            search_url = f"{self.base_url}esearch.fcgi"
            params = {
                "db": database,
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "tool": "genoscope",
                "email": "researcher@example.com",
                "usehistory": "y"  # Use history for better SRA results
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        ids = data.get("esearchresult", {}).get("idlist", [])
                        
                        if not ids:
                            return []
                        
                        # Step 2: For SRA, use efetch instead of esummary for better data
                        if database == "sra":
                            return await self._get_sra_details(ids)
                        else:
                            return await self._get_summaries(ids, database)
                    else:
                        return []
        
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]
    
    async def _get_summaries(self, ids: List[str], database: str) -> List[Dict[str, Any]]:
        """Get detailed summaries for a list of IDs"""
        summary_url = f"{self.base_url}esummary.fcgi"
        params = {
            "db": database,
            "id": ",".join(ids),
            "retmode": "json",
            "tool": "genoscope",
            "email": "researcher@example.com"
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        async with aiohttp.ClientSession() as session:
            async with session.get(summary_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for uid, summary in data.get("result", {}).items():
                        if uid == "uids":
                            continue
                            
                        # Extract relevant information based on database
                        result = self._parse_summary(summary, database)
                        if result:
                            results.append(result)
                    
                    return results
                else:
                    return []
    
    async def _get_sra_details(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Get SRA details using efetch for better accession extraction"""
        fetch_url = f"{self.base_url}efetch.fcgi"
        params = {
            "db": "sra",
            "id": ",".join(ids),
            "rettype": "runinfo",
            "retmode": "text",
            "tool": "genoscope",
            "email": "researcher@example.com"
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        async with aiohttp.ClientSession() as session:
            async with session.get(fetch_url, params=params) as response:
                if response.status == 200:
                    text = await response.text()
                    return self._parse_sra_runinfo(text)
                else:
                    return []
    
    def _parse_sra_runinfo(self, runinfo_text: str) -> List[Dict[str, Any]]:
        """Parse SRA runinfo CSV format"""
        results = []
        lines = runinfo_text.strip().split('\n')
        
        if len(lines) < 2:
            return []
        
        # Parse header
        header = lines[0].split(',')
        
        # Parse each run
        for line in lines[1:]:
            fields = line.split(',')
            if len(fields) < len(header):
                continue
            
            # Create dict from header and fields
            run_data = dict(zip(header, fields))
            
            result = {
                "id": run_data.get("Run", ""),
                "accession": run_data.get("Run", ""),
                "title": f"{run_data.get('SampleName', 'Unknown')} - {run_data.get('LibraryStrategy', 'RNA-Seq')}",
                "organism": run_data.get("ScientificName", run_data.get("Organism", "Unknown")),
                "study_type": run_data.get("LibraryStrategy", "RNA-Seq"),
                "platform": run_data.get("Platform", "Unknown"),
                "experiment": run_data.get("Experiment", ""),
                "study": run_data.get("SRAStudy", ""),
                "type": "sequencing_run",
                "database": "sra"
            }
            results.append(result)
        
        return results
    
    def _parse_summary(self, summary: Dict, database: str) -> Optional[Dict[str, Any]]:
        """Parse summary data based on database type"""
        try:
            if database == "nuccore":
                return {
                    "id": summary.get("uid", ""),
                    "accession": summary.get("accessionversion", ""),
                    "title": summary.get("title", ""),
                    "organism": summary.get("organism", ""),
                    "length": summary.get("slen", 0),
                    "type": "nucleotide_sequence",
                    "database": database
                }
            
            elif database == "protein":
                return {
                    "id": summary.get("uid", ""),
                    "accession": summary.get("accessionversion", ""),
                    "title": summary.get("title", ""),
                    "organism": summary.get("organism", ""),
                    "length": summary.get("slen", 0),
                    "type": "protein_sequence", 
                    "database": database
                }
            
            elif database == "sra":
                # SRA has different field names - need to extract properly
                expxml = summary.get("expxml", "")
                runs = summary.get("runs", "")
                
                # Try to get accession from runs or expxml
                accession = ""
                if runs and "@acc=" in runs:
                    # Extract accession from runs string
                    import re
                    acc_match = re.search(r'@acc="([^"]+)"', runs)
                    if acc_match:
                        accession = acc_match.group(1)
                
                # Fallback to other fields
                if not accession:
                    accession = summary.get("accession", summary.get("uid", ""))
                
                return {
                    "id": summary.get("uid", ""),
                    "accession": accession,
                    "title": summary.get("title", expxml[:100] if expxml else "No title"),
                    "organism": summary.get("organism", "Unknown"),
                    "study_type": summary.get("study_type", "RNA-Seq"),
                    "platform": summary.get("platform", "Unknown"),
                    "type": "sequencing_run",
                    "database": database
                }
            
            return None
            
        except Exception as e:
            return {"error": f"Failed to parse summary: {str(e)}"}
    
    async def search_geo_datasets(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search GEO datasets using NCBI E-utilities
        
        Args:
            query: Search terms (e.g., "breast cancer RNA-seq", "Alzheimer")
            max_results: Maximum number of results
        """
        try:
            # Search GEO DataSets database
            search_url = f"{self.base_url}esearch.fcgi"
            params = {
                "db": "gds",
                "term": f"{query}[All Fields]",
                "retmax": max_results,
                "retmode": "json",
                "tool": "genoscope",
                "email": "researcher@example.com"
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        ids = data.get("esearchresult", {}).get("idlist", [])
                        
                        if not ids:
                            return []
                        
                        # Get summaries for GEO datasets
                        return await self._get_geo_summaries(ids)
                    else:
                        return []
        
        except Exception as e:
            return [{"error": f"GEO search failed: {str(e)}"}]
    
    async def _get_geo_summaries(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Get GEO dataset summaries"""
        summary_url = f"{self.base_url}esummary.fcgi"
        params = {
            "db": "gds",
            "id": ",".join(ids),
            "retmode": "json",
            "version": "2.0",
            "tool": "genoscope",
            "email": "researcher@example.com"
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        async with aiohttp.ClientSession() as session:
            async with session.get(summary_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for uid, summary in data.get("result", {}).items():
                        if uid == "uids":
                            continue
                        
                        geo_result = {
                            "id": summary.get("uid", ""),
                            "accession": summary.get("accession", ""),
                            "title": summary.get("title", ""),
                            "summary": summary.get("summary", ""),
                            "organism": summary.get("taxon", ""),
                            "study_type": summary.get("gdstype", ""),
                            "samples_count": summary.get("n_samples", 0),
                            "platform": summary.get("gpl", ""),
                            "type": "expression_dataset",
                            "database": "geo"
                        }
                        results.append(geo_result)
                    
                    return results
                else:
                    return []
    
    async def download_sequences(self, accessions: List[str], 
                               format_type: str = "fasta") -> Dict[str, str]:
        """
        Download sequences in specified format
        
        Args:
            accessions: List of accession numbers
            format_type: Output format (fasta, gb, xml)
        """
        try:
            fetch_url = f"{self.base_url}efetch.fcgi"
            params = {
                "db": "nuccore",
                "id": ",".join(accessions),
                "rettype": format_type,
                "retmode": "text",
                "tool": "genoscope",
                "email": "researcher@example.com"
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.get(fetch_url, params=params) as response:
                    if response.status == 200:
                        content = await response.text()
                        return {
                            "format": format_type,
                            "content": content,
                            "accessions": accessions
                        }
                    else:
                        return {"error": f"Download failed with status {response.status}"}
        
        except Exception as e:
            return {"error": f"Download failed: {str(e)}"}
    
    async def get_study_details(self, accession: str) -> Dict[str, Any]:
        """Get detailed information about a specific study"""
        try:
            # Try different databases to find the accession
            databases = ["sra", "gds", "nuccore", "protein"]
            
            for db in databases:
                search_url = f"{self.base_url}esearch.fcgi"
                params = {
                    "db": db,
                    "term": f"{accession}[ACCN]",
                    "retmode": "json",
                    "tool": "genoscope",
                    "email": "researcher@example.com"
                }
                
                if self.api_key:
                    params["api_key"] = self.api_key
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(search_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            ids = data.get("esearchresult", {}).get("idlist", [])
                            
                            if ids:
                                summaries = await self._get_summaries(ids, db)
                                if summaries:
                                    return summaries[0]
            
            return {"error": f"Accession {accession} not found in any database"}
        
        except Exception as e:
            return {"error": f"Failed to get study details: {str(e)}"}

# Example usage and testing
async def main():
    """Test the NCBI MCP Server"""
    server = NCBIMCPServer()
    
    print("=== Testing NCBI MCP Server ===\n")
    
    # Test 1: Search for COVID-19 RNA-seq data
    print("1. Searching for COVID-19 RNA-seq data...")
    covid_results = await server.search_genomics_data(
        "COVID-19 RNA-seq", 
        database="sra", 
        max_results=5
    )
    print(f"Found {len(covid_results)} results")
    for result in covid_results[:2]:  # Show first 2
        print(f"  - {result.get('accession', 'N/A')}: {result.get('title', 'N/A')[:80]}...")
    
    # Test 2: Search GEO datasets
    print("\n2. Searching GEO for breast cancer datasets...")
    geo_results = await server.search_geo_datasets("breast cancer", max_results=3)
    print(f"Found {len(geo_results)} GEO datasets")
    for result in geo_results:
        print(f"  - {result.get('accession', 'N/A')}: {result.get('title', 'N/A')[:80]}...")
    
    # Test 3: Download a sequence
    print("\n3. Downloading BRCA1 sequence...")
    brca1_seq = await server.download_sequences(["NM_007294"], "fasta")
    if "content" in brca1_seq:
        print(f"Downloaded sequence ({len(brca1_seq['content'])} characters)")
        print(f"First 200 characters:\n{brca1_seq['content'][:200]}...")
    else:
        print(f"Download failed: {brca1_seq.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())
