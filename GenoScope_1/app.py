#!/usr/bin/env python3
"""
GenoScope Web Interface
Beautiful Streamlit app for genomics data search
"""

import streamlit as st
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from genomics_query_agent import GenomicsQueryAgent

# Configure page
st.set_page_config(
    page_title="GenoScope - AI Genomics Search",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .result-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #0066cc;
    }
    .metric-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize agent (cached)
@st.cache_resource
def get_agent():
    return GenomicsQueryAgent()

def main():
    # Header
    st.markdown('<p class="main-header">🧬 GenoScope</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Genomics Data Discovery</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📚 About GenoScope")
        st.markdown("""
        GenoScope uses AI to search genomics databases using natural language.
        
        **Just describe what you're looking for!**
        
        ### Example Queries:
        - Find human breast cancer RNA-seq data
        - Show me mouse Alzheimer studies
        - COVID-19 protein sequences
        - Zebrafish development datasets
        """)
        
        st.divider()
        
        st.header("🔧 Settings")
        max_results = st.slider("Max results per database", 5, 20, 10)
        
        st.divider()
        
        # API Key status
        api_key = os.getenv("NCBI_API_KEY")
        if api_key:
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ No API key set (slower rate limit)")
            st.info("Set with: `set NCBI_API_KEY=your_key`")
    
    # Main search interface
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Search input
        query = st.text_input(
            "What genomics data are you looking for?",
            placeholder="e.g., Find human cancer RNA-seq data",
            label_visibility="collapsed",
            key="search_query"
        )
        
        # Example queries as buttons
        st.markdown("**Quick examples:**")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🧬 Breast Cancer RNA-seq"):
                st.session_state.search_query = "Find human breast cancer RNA-seq data"
                st.rerun()
        
        with col_b:
            if st.button("🐭 Mouse Alzheimer"):
                st.session_state.search_query = "Show me mouse Alzheimer studies"
                st.rerun()
        
        with col_c:
            if st.button("🦠 COVID-19 Proteins"):
                st.session_state.search_query = "COVID-19 protein sequences"
                st.rerun()
    
    # Search button
    if query:
        with st.spinner("🔍 Searching genomics databases..."):
            try:
                # Run async search
                agent = get_agent()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(agent.process_query(query))
                
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                    return
                
                # Display parsed intent
                intent = result.get('parsed_intent', {})
                
                st.success("✅ Search complete!")
                
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Data Type", intent.get('data_type', 'Unknown').replace('_', '-').upper())
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Organism", intent.get('organism', 'Unknown').capitalize())
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Condition", intent.get('condition', 'Not specified').capitalize())
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    results = result.get('results', [])
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Results Found", len(results))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.divider()
                
                # Display results
                if results:
                    st.header("📊 Search Results")
                    
                    # Sort options
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        sort_by = st.selectbox(
                            "Sort by",
                            ["Relevance", "Accession", "Database"],
                            label_visibility="collapsed"
                        )
                    
                    # Display each result
                    for i, res in enumerate(results, 1):
                        with st.expander(
                            f"**{i}. {res['accession']}** - {res['title'][:80]}{'...' if len(res['title']) > 80 else ''}",
                            expanded=(i == 1)  # First result expanded by default
                        ):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**Title:** {res['title']}")
                                st.markdown(f"**Organism:** {res['organism']}")
                                st.markdown(f"**Type:** {res['type'].replace('_', ' ').title()}")
                                st.markdown(f"**Database:** {res['database'].upper()}")
                                
                                if res.get('summary'):
                                    st.markdown(f"**Summary:** {res['summary']}")
                            
                            with col2:
                                # Relevance score with color
                                score = res['relevance_score']
                                if score >= 0.7:
                                    st.success(f"🎯 Relevance\n## {score:.2f}")
                                elif score >= 0.5:
                                    st.info(f"📊 Relevance\n## {score:.2f}")
                                else:
                                    st.warning(f"📉 Relevance\n## {score:.2f}")
                                
                                st.link_button("📥 Download", res['download_url'], use_container_width=True)
                    
                    # Recommendations
                    recommendations = result.get('recommendations', [])
                    if recommendations:
                        st.divider()
                        st.header("💡 Recommendations")
                        for rec in recommendations:
                            st.info(f"• {rec}")
                    
                    # Export results
                    st.divider()
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        if st.button("📋 Copy All Links", use_container_width=True):
                            links = "\n".join([f"{r['accession']}: {r['download_url']}" for r in results])
                            st.code(links)
                    
                    with col2:
                        # Create downloadable CSV
                        import pandas as pd
                        df = pd.DataFrame(results)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"genoscope_results_{query[:20]}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                else:
                    st.warning("No results found. Try rephrasing your query or using broader terms.")
                    
                    st.info("""
                    **Tips for better results:**
                    - Be specific about organism (human, mouse, etc.)
                    - Include data type (RNA-seq, protein, genome)
                    - Mention condition or phenotype
                    """)
                
            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")
                st.info("Make sure your API key is configured correctly.")
    
    else:
        # Welcome screen when no query
        st.info("👆 Enter a query above or click one of the example buttons to get started!")
        
        # Show some stats or features
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🔍 Smart Search")
            st.markdown("Natural language understanding powered by AI")
        
        with col2:
            st.markdown("### 🗄️ Multi-Database")
            st.markdown("Searches NCBI, GEO, SRA automatically")
        
        with col3:
            st.markdown("### 📊 Ranked Results")
            st.markdown("Results sorted by biological relevance")

    # Footer
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            Built with ❤️ using Streamlit • 
            <a href='https://github.com/aleszcz/genoscope'>View on GitHub</a>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
