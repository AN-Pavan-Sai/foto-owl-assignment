from langgraph.graph import StateGraph, END
from typing import Literal
from src.state import GraphState
from src.agents.nodes import (
    intent_parser_node,
    image_analyser_node,
    storyboard_writer_node,
    script_generator_node,
    compiler_fixer_node,
    renderer_node
)

MAX_RETRIES = 3

def should_retry_compile(state: GraphState) -> Literal["script_generator_node", "renderer_node", "end"]:
    print("--- Conditional Routing ---")
    if state.get("compile_error"):
        if state.get("retry_count", 0) < MAX_RETRIES:
            print(f"Compilation failed. Retrying... (Attempt {state.get('retry_count')})")
            return "script_generator_node"
        else:
            print("Max retries reached. Exiting with failure.")
            return "end"
    
    print("Compilation successful. Proceeding to render.")
    return "renderer_node"

def build_graph():
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("intent_parser_node", intent_parser_node)
    workflow.add_node("image_analyser_node", image_analyser_node)
    workflow.add_node("storyboard_writer_node", storyboard_writer_node)
    workflow.add_node("script_generator_node", script_generator_node)
    workflow.add_node("compiler_fixer_node", compiler_fixer_node)
    workflow.add_node("renderer_node", renderer_node)

    # Build the graph
    workflow.set_entry_point("intent_parser_node")
    workflow.add_edge("intent_parser_node", "image_analyser_node")
    workflow.add_edge("image_analyser_node", "storyboard_writer_node")
    workflow.add_edge("storyboard_writer_node", "script_generator_node")
    workflow.add_edge("script_generator_node", "compiler_fixer_node")
    
    # Conditional edge
    workflow.add_conditional_edges(
        "compiler_fixer_node",
        should_retry_compile,
        {
            "script_generator_node": "script_generator_node",
            "renderer_node": "renderer_node",
            "end": END
        }
    )
    
    workflow.add_edge("renderer_node", END)

    # Compile the graph
    app = workflow.compile()
    return app
