#!/usr/bin/env python3
"""
Simple NCBI Test Script
Tests your GenoScope setup with a real NCBI query
Usage: python test_ncbi.py
"""

import asyncio
import aiohttp
import os
from datetime import datetime

async def test_ncbi_connection():
    """Test basic NCBI connection and search"""
    
    print("=" * 60)
    print("  🧬 GenoScope NCBI Connection Test")
    print("=" * 60)
    print()
    
    # Check API key
    api_key = os.getenv("NCBI_API_KEY")
    if api_key:
        print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("⚠️  No API Key set (will use slower rate limit)")
        print("   Set it with: set NCBI_API_KEY=your_key")
    
    print()
    print("Testing NCBI E-utilities connection...")
    print("-" * 60)
    
    # Simple search for COVID-19 sequences
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi"
    
    params = {
        "db": "nuccore",
        "term": "COVID-19[All Fields]",
        "retmax": 5,
        "retmode": "json",
        "tool": "genoscope_test",
        "email": "test@example.com"
    }
    
    if api_key:
        params["api_key"] = api_key
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"\n🔍 Searching for: {params['term']}")
            print(f"📚 Database: {params['db']}")
            
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get("esearchresult", {})
                    count = result.get("count", "0")
                    ids = result.get("idlist", [])
                    
                    print(f"\n✅ Connection successful!")
                    print(f"   Total results: {count}")
                    print(f"   Retrieved IDs: {len(ids)}")
                    
                    if ids:
                        print(f"\n📋 First few IDs: {', '.join(ids[:3])}")
                        
                        # Get details for first result
                        print(f"\n📊 Fetching details for ID: {ids[0]}...")
                        summary_url = f"{base_url}esummary.fcgi"
                        summary_params = {
                            "db": "nuccore",
                            "id": ids[0],
                            "retmode": "json"
                        }
                        if api_key:
                            summary_params["api_key"] = api_key
                        
                        async with session.get(summary_url, params=summary_params) as sum_response:
                            if sum_response.status == 200:
                                sum_data = await sum_response.json()
                                result_data = sum_data.get("result", {}).get(ids[0], {})
                                
                                print(f"\n   Accession: {result_data.get('accessionversion', 'N/A')}")
                                print(f"   Title: {result_data.get('title', 'N/A')[:80]}...")
                                print(f"   Organism: {result_data.get('organism', 'N/A')}")
                                print(f"   Length: {result_data.get('slen', 'N/A')} bp")
                    
                    print("\n" + "=" * 60)
                    print("✅ NCBI connection test PASSED!")
                    print("\nYour GenoScope setup is working correctly!")
                    print("\nNext steps:")
                    print("1. Copy ncbi_mcp_server.py to src/ folder")
                    print("2. Copy genomics_query_agent.py to src/ folder")
                    print("3. Try running the full MCP server")
                    print("=" * 60)
                    
                else:
                    print(f"\n❌ Request failed with status: {response.status}")
                    print(f"   Response: {await response.text()}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify your API key is correct")
        print("3. Try again in a few moments")

if __name__ == "__main__":
    asyncio.run(test_ncbi_connection())
