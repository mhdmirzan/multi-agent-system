from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from rich import print 

def run_research_pipeline(topic: str) -> str:
    
    state = {}
    
    # Step 1: Search Agent
    print("\n"+ "="*50)
    print("[bold blue]Step 1: Search Agent is working ...[/bold blue]")
    print("\n"+ "="*50)
    
    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        "messages": ["user", f"Find recent, reliable and detailed information about: {topic}"]
    }) 
    state["search_results"] = search_results['messages'][-1].content 
    print("[green]Search Results:[/green]", state["search_results"])
    
    # Step 2: Reader Agent
    print("\n"+ "="*50) 
    print("[bold blue]Step 2: Reader Agent is scraping top resources ...[/bold blue]")
    print("\n"+ "="*50)
    
    reader_agent = build_reader_agent()
    reader_results = reader_agent.invoke({
        "messages": [("user",
             f"Based on the following search results about '{topic}', " 
             f"pick the most relevant URL and scrape it for deeper content. \n\n"
             f"Search Results:\n{state['search_results'][:800]}"
            )]
    })
    state["scraped_content"] = reader_results['messages'][-1].content
    print("[green]Scraped Content:[/green]", state["scraped_content"])
    
    # Step 3: Writer report
    print("\n"+ "="*50)
    print("[bold blue]Step 3: Writer Chain is drafting the report ...[/bold blue]")
    print("\n"+ "="*50)

    research_combined = (
        f"SEARCH RESULTS:\n {state['search_results']}\n\n"
        f"SCRAPED CONTENT:\n {state['scraped_content']}"
    )
    
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })
    
    print("[green] Final Report:[/green]", state["report"])
    
    # Step 4: Critic report
    print("\n"+ "="*50)
    print("[bold blue]Step 4: Critic Chain is reviewing the report [/bold blue]")
    print("\n"+ "="*50)
    
    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })
    
    print("[green] Critic Report:[/green]", state["feedback"])
    
    return state



if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)
