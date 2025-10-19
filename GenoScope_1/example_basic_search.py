#!/usr/bin/env python3
"""
Basic GenoScope Search Example
Demonstrates how to use GenoScope for genomics data discovery
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from genomics_query_agent import GenomicsQueryAgent

async def basic_search_example():
    """Run a basic search example"""
    
    # Initialize the agent
    agent = GenomicsQueryAgent()
    
    # Example query
    query = "Find human breast cancer RNA-seq data"
    
    print("=" * 70)
    print(f"  🧬 GenoScope Basic Search Example")
    print("=" * 70)
    print(f"\nQuery: '{query}'")
    print("-" * 70)
    
    # Process the query
    result = await agent.process_query(query)
    
    # Display results
    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        return
    
    # Show what was detected
    intent = result['parsed_intent']
    print(f"\n📊 Detected Query Intent:")
    print(f"   • Data Type: {intent['data_type']}")
    print(f"   • Organism: {intent['organism']}")
    print(f"   • Condition: {intent['condition']}")
    
    # Show results
    results = result.get('results', [])
    print(f"\n🔍 Found {len(results)} results")
    print("-" * 70)
    
    if results:
        for i, res in enumerate(results[:5], 1):  # Show top 5
            print(f"\n{i}. {res['accession']}")
            print(f"   Title: {res['title'][:65]}...")
            print(f"   Organism: {res['organism']}")
            print(f"   Database: {res['database'].upper()}")
            print(f"   Relevance: {res['relevance_score']:.2f}")
            print(f"   🔗 {res['download_url']}")
    
    # Show recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    print("\n" + "=" * 70)
    print("✅ Search complete!")
    print("=" * 70)

async def custom_query_example():
    """Example with custom query"""
    
    agent = GenomicsQueryAgent()
    
    # Try your own query here!
    custom_query = "Show me mouse Alzheimer studies"
    
    print("\n\n" + "=" * 70)
    print(f"  🔬 Custom Query Example")
    print("=" * 70)
    print(f"\nQuery: '{custom_query}'")
    
    result = await agent.process_query(custom_query)
    
    if "error" not in result:
        results = result.get('results', [])
        print(f"\n✅ Found {len(results)} results")
        
        for i, res in enumerate(results[:3], 1):
            print(f"\n{i}. {res['accession']}: {res['title'][:60]}...")
            print(f"   Download: {res['download_url']}")

async def multiple_queries_example():
    """Example with multiple queries"""
    
    agent = GenomicsQueryAgent()
    
    queries = [
        "COVID-19 protein sequences",
        "Zebrafish development RNA-seq",
        "Mouse diabetes gene expression"
    ]
    
    print("\n\n" + "=" * 70)
    print(f"  📚 Multiple Queries Example")
    print("=" * 70)
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        result = await agent.process_query(query)
        
        if "error" not in result:
            count = len(result.get('results', []))
            print(f"   ✅ Found {count} results")
        else:
            print(f"   ❌ Error: {result['error']}")

async def main():
    """Run all examples"""
    
    # Check API key
    if not os.getenv("NCBI_API_KEY"):
        print("⚠️  Warning: NCBI_API_KEY not set")
        print("   Set it with: export NCBI_API_KEY=your_key")
        print("   Continuing with rate-limited access...\n")
    
    # Run examples
    await basic_search_example()
    await custom_query_example()
    await multiple_queries_example()
    
    print("\n" + "=" * 70)
    print("  🎉 All examples complete!")
    print("=" * 70)
    print("\n💡 Try modifying the queries in this script to search")
    print("   for datasets relevant to your research!\n")

if __name__ == "__main__":
    asyncio.run(main())
