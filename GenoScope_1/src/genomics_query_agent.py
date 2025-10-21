#!/usr/bin/env python3
"""
Genomics Query Agent - AI agent that understands natural language queries
and converts them to structured database searches using MCP servers
"""

import asyncio
import sys
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add parent directory to path to import ncbi_mcp_server
sys.path.insert(0, os.path.dirname(__file__))
from ncbi_mcp_server import NCBIMCPServer

@dataclass
class QueryIntent:
    """Structured representation of user query intent"""
    data_type: str  # "rna_seq", "dna_seq", "protein", "expression"
    organism: str   # "human", "mouse", etc.
    condition: str  # "cancer", "alzheimer", etc.
    study_type: str # "case_control", "time_series", etc.
    keywords: List[str]
    confidence: float

class GenomicsQueryAgent:
    """AI Agent that processes natural language genomics queries"""
    
    def __init__(self):
        self.ncbi_server = NCBIMCPServer()
        
        # Biological entity patterns for simple NLP
        self.organisms = {
            "human": ["human", "homo sapiens", "people", "patient"],
            "mouse": ["mouse", "mice", "mus musculus", "murine"],
            "rat": ["rat", "rattus", "rodent"],
            "zebrafish": ["zebrafish", "danio rerio"],
            "drosophila": ["fly", "flies", "drosophila", "fruit fly"],
            "yeast": ["yeast", "saccharomyces", "cerevisiae"]
        }
        
        self.data_types = {
            "rna_seq": ["rna-seq", "rna seq", "transcriptome", "expression", "gene expression"],
            "dna_seq": ["dna-seq", "genome", "genomic", "whole genome", "dna"],
            "protein": ["protein", "proteome", "proteomic"],
            "chip_seq": ["chip-seq", "chromatin", "histone", "binding"],
            "single_cell": ["single cell", "scRNA-seq", "single-cell"]
        }
        
        self.sample_types = {
            "clinical": ["biopsy", "biopsies", "tissue", "primary", "patient", "clinical"],
            "cell_line": ["cell line", "MCF", "HeLa", "culture", "cultured"]
        }
        
        self.conditions = {
            "cancer": ["cancer", "tumor", "carcinoma", "oncology", "malignant", "breast cancer"],
            "alzheimer": ["alzheimer", "dementia", "neurodegenerative"],
            "diabetes": ["diabetes", "diabetic", "glucose", "insulin"],
            "covid": ["covid", "coronavirus", "sars-cov-2", "pandemic"],
            "heart_disease": ["cardiac", "heart", "cardiovascular", "coronary"]
        }
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main function to process natural language query and return results
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Structured results with data recommendations
        """
        try:
            print(f"\n🔍 Processing query: '{user_query}'")
            print("-" * 60)
            
            # Step 1: Parse user intent
            intent = self._parse_query_intent(user_query)
            print(f"📊 Detected: {intent.data_type} | {intent.organism} | {intent.condition}")
            
            # Step 2: Generate database queries
            search_strategies = self._generate_search_strategies(intent)
            print(f"🎯 Using {len(search_strategies)} search strategies")
            
            # Step 3: Execute searches using MCP server
            results = await self._execute_searches(search_strategies)
            print(f"✅ Found {len(results)} total results")
            
            # Step 4: Rank and format results
            formatted_results = self._format_results(results, intent)
            
            return {
                "original_query": user_query,
                "parsed_intent": intent.__dict__,
                "search_strategies": search_strategies,
                "results": formatted_results,
                "recommendations": self._generate_recommendations(formatted_results, intent)
            }
            
        except Exception as e:
            return {
                "error": f"Query processing failed: {str(e)}",
                "original_query": user_query
            }
    
    def _parse_query_intent(self, query: str) -> QueryIntent:
        """Parse natural language query to extract structured intent"""
        query_lower = query.lower()
        
        # Simple pattern matching
        detected_organism = "human"  # default
        detected_data_type = "rna_seq"  # default
        detected_condition = ""
        keywords = []
        
        # Detect organism
        for organism, patterns in self.organisms.items():
            if any(pattern in query_lower for pattern in patterns):
                detected_organism = organism
                break
        
        # Detect data type
        for data_type, patterns in self.data_types.items():
            if any(pattern in query_lower for pattern in patterns):
                detected_data_type = data_type
                break
        
        # Detect condition
        for condition, patterns in self.conditions.items():
            if any(pattern in query_lower for pattern in patterns):
                detected_condition = condition
                break
        
        # Extract key terms
        keywords = self._extract_keywords(query)
        
        return QueryIntent(
            data_type=detected_data_type,
            organism=detected_organism,
            condition=detected_condition,
            study_type="",
            keywords=keywords,
            confidence=0.8
        )
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        stop_words = {"the", "and", "or", "for", "in", "with", "of", "to", "from", "a", "an", "find", "show", "get"}
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords[:10]
    
    def _generate_search_strategies(self, intent: QueryIntent) -> List[Dict[str, Any]]:
        """Generate multiple search strategies based on parsed intent"""
        strategies = []
        
        # Strategy 1: Specific tissue/clinical sample search
        if "biopsy" in " ".join(intent.keywords) or "tissue" in " ".join(intent.keywords):
            # Search for primary tissue samples, exclude cell lines
            clinical_query = f"{intent.organism} {intent.condition} {intent.data_type} (biopsy OR tissue OR primary) NOT (cell line OR MCF OR HeLa OR culture)"
            strategies.append({
                "strategy": "clinical_samples",
                "query": clinical_query,
                "database": self._select_database(intent.data_type),
                "priority": 1
            })
        else:
            # Standard direct search
            main_query = f"{intent.organism} {intent.condition} {intent.data_type}".strip()
            strategies.append({
                "strategy": "direct_keywords",
                "query": main_query,
                "database": self._select_database(intent.data_type),
                "priority": 1
            })
        
        # Strategy 2: GEO-specific search for expression data with tissue filter
        if intent.data_type in ["rna_seq", "expression"]:
            if "biopsy" in " ".join(intent.keywords) or "tissue" in " ".join(intent.keywords):
                geo_query = f"{intent.condition} {intent.organism} (tissue OR biopsy OR primary) NOT (cell line)"
            else:
                geo_query = f"{intent.condition} {intent.organism}".strip()
            
            if geo_query:
                strategies.append({
                    "strategy": "geo_expression",
                    "query": geo_query,
                    "database": "geo",
                    "priority": 2
                })
        
        return strategies
    
    def _select_database(self, data_type: str) -> str:
        """Select appropriate database based on data type"""
        database_map = {
            "rna_seq": "sra",
            "dna_seq": "nuccore", 
            "protein": "protein",
            "chip_seq": "sra",
            "single_cell": "sra"
        }
        return database_map.get(data_type, "nuccore")
    
    async def _execute_searches(self, strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute search strategies using MCP server"""
        all_results = []
        
        for strategy in strategies:
            try:
                if strategy["database"] == "geo":
                    results = await self.ncbi_server.search_geo_datasets(
                        strategy["query"], 
                        max_results=5
                    )
                else:
                    results = await self.ncbi_server.search_genomics_data(
                        strategy["query"],
                        database=strategy["database"],
                        max_results=5
                    )
                
                # Add metadata to results
                for result in results:
                    result["search_strategy"] = strategy["strategy"]
                    result["priority"] = strategy["priority"]
                
                all_results.extend(results)
                
            except Exception as e:
                print(f"⚠️  Search strategy {strategy['strategy']} failed: {e}")
                continue
        
        return all_results
    
    def _format_results(self, results: List[Dict[str, Any]], intent: QueryIntent) -> List[Dict[str, Any]]:
        """Format and rank results based on relevance"""
        
        # Score results based on relevance
        scored_results = []
        for result in results:
            score = self._calculate_relevance_score(result, intent)
            result["relevance_score"] = score
            scored_results.append(result)
        
        # Sort by relevance score
        scored_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Format for user display
        formatted = []
        for result in scored_results[:10]:  # Top 10 results
            formatted_result = {
                "accession": result.get("accession", "N/A"),
                "title": result.get("title", "No title"),
                "organism": result.get("organism", "Unknown"),
                "type": result.get("type", "Unknown"),
                "database": result.get("database", "Unknown"),
                "relevance_score": result.get("relevance_score", 0),
                "summary": result.get("summary", "")[:200],
                "download_url": self._generate_download_url(result)
            }
            formatted.append(formatted_result)
        
        return formatted
    
    def _calculate_relevance_score(self, result: Dict[str, Any], intent: QueryIntent) -> float:
        """Calculate relevance score for a result"""
        score = 0.0
        
        # Base score from search priority
        score += (4 - result.get("priority", 4)) * 0.2
        
        # Organism match
        if intent.organism.lower() in result.get("organism", "").lower():
            score += 0.3
        
        # Data type match
        result_title = result.get("title", "").lower()
        if intent.data_type in ["rna_seq", "expression"] and any(term in result_title for term in ["rna", "expression", "transcriptome"]):
            score += 0.2
        
        # Condition/keyword match in title
        for keyword in intent.keywords:
            if keyword.lower() in result_title:
                score += 0.1
        
        return min(score, 1.0)
    
    def _generate_download_url(self, result: Dict[str, Any]) -> str:
        """Generate download URL for a result"""
        accession = result.get("accession", "")
        database = result.get("database", "")
        
        if database == "geo":
            return f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}"
        elif database == "sra":
            return f"https://www.ncbi.nlm.nih.gov/sra/{accession}"
        else:
            return f"https://www.ncbi.nlm.nih.gov/nuccore/{accession}"
    
    def _generate_recommendations(self, results: List[Dict[str, Any]], intent: QueryIntent) -> List[str]:
        """Generate helpful recommendations based on results"""
        recommendations = []
        
        if not results:
            recommendations.append("No results found. Try broader search terms.")
            return recommendations
        
        # Analyze result patterns
        databases = set(r.get("database") for r in results)
        
        if "geo" in databases:
            recommendations.append("Found GEO expression datasets - great for comparative analysis")
        
        if "sra" in databases:
            recommendations.append("Found SRA sequencing data - download raw FASTQ files available")
        
        # High-quality result recommendations
        high_quality = [r for r in results if r.get("relevance_score", 0) > 0.5]
        if high_quality:
            recommendations.append(f"Found {len(high_quality)} highly relevant datasets")
        
        return recommendations

# Example usage and testing
async def main():
    """Test the Genomics Query Agent"""
    agent = GenomicsQueryAgent()
    
    print("=" * 60)
    print("  🧬 GenoScope Query Agent Test")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "Find RNA-seq data for breast cancer in humans",
        "Show me mouse Alzheimer's disease studies",
        "COVID-19 protein sequences"
    ]
    
    for query in test_queries:
        result = await agent.process_query(query)
        
        print(f"\n📋 Top Results:")
        if "results" in result and result["results"]:
            for i, res in enumerate(result['results'][:3], 1):
                print(f"   {i}. [{res['relevance_score']:.2f}] {res['accession']}")
                print(f"      {res['title'][:70]}...")
                print(f"      🔗 {res['download_url']}")
        
        if "recommendations" in result:
            print(f"\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"   • {rec}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
