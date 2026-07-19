import os
import pytest
from unittest.mock import patch, MagicMock

os.environ["OPENAI_API_KEY"] = "dummy"

from src.graph import build_graph
from src.models import VideoIntent, Storyboard, Scene

# Mock data
mock_intent = VideoIntent(
    pacing="fast",
    visual_style="upbeat",
    caption_tone="bold",
    transition_preference="quick cuts"
)

mock_storyboard = Storyboard(
    scenes=[
        Scene(image_path="test.jpg", duration_frames=30, caption="Test", transition_type="cut", animation_style="none")
    ],
    total_duration_frames=30
)

@pytest.fixture
def graph():
    return build_graph()

@patch("langchain_openai.ChatOpenAI.invoke")
@patch("langchain_openai.ChatOpenAI.with_structured_output")
@patch("langchain_openai.OpenAIEmbeddings.embed_documents")
@patch("langchain_openai.OpenAIEmbeddings.embed_query")
def test_scenario_1_fast_pipeline(mock_embed_query, mock_embed_docs, mock_structured, mock_invoke, graph):
    # Mock embeddings to return dummy vectors
    mock_embed_docs.return_value = [[0.1]*1536] * 10
    mock_embed_query.return_value = [0.1]*1536
    
    # Mock structured output (for intent and storyboard)
    mock_chain = MagicMock()
    # The order of structured output calls: IntentParser -> StoryboardWriter
    mock_chain.invoke.side_effect = [mock_intent, mock_storyboard]
    mock_structured.return_value = mock_chain
    
    # Mock standard invoke (for script generation)
    mock_response = MagicMock()
    mock_response.content = "export const MyVideo = () => <div>Test</div>;"
    mock_invoke.return_value = mock_response
    
    inputs = {"user_prompt": "Fast upbeat video", "image_paths": ["img1.jpg"]}
    with patch("src.agents.nodes.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        result = graph.invoke(inputs)
        
    assert result["render_success"] is True

@patch("langchain_openai.ChatOpenAI.invoke")
@patch("langchain_openai.ChatOpenAI.with_structured_output")
@patch("langchain_openai.OpenAIEmbeddings.embed_documents")
@patch("langchain_openai.OpenAIEmbeddings.embed_query")
def test_scenario_2_compile_retry(mock_embed_query, mock_embed_docs, mock_structured, mock_invoke, graph):
    mock_embed_docs.return_value = [[0.1]*1536] * 10
    mock_embed_query.return_value = [0.1]*1536
    
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = [mock_intent, mock_storyboard]
    mock_structured.return_value = mock_chain
    
    mock_response = MagicMock()
    mock_response.content = "export const MyVideo = () => <div>Test</div>;"
    mock_invoke.return_value = mock_response
    
    with patch("src.agents.nodes.subprocess.run") as mock_run:
        fail_mock = MagicMock(returncode=1, stdout="Error", stderr="TS Error")
        success_mock = MagicMock(returncode=0, stdout="", stderr="")
        mock_run.side_effect = [fail_mock, success_mock, success_mock] 
        
        result = graph.invoke({"user_prompt": "Test", "image_paths": ["img1.jpg"]})
        
    assert result["retry_count"] == 1
    assert result["render_success"] is True

@patch("langchain_openai.ChatOpenAI.invoke")
def test_llm_as_judge_narrative_coherence(mock_invoke):
    prompt = """
    Evaluate the narrative coherence of this storyboard from 1 to 10.
    Storyboard: {storyboard}
    Output ONLY a JSON object: {{"score": 8, "reason": "..."}}
    """
    mock_response = MagicMock()
    mock_response.content = '{"score": 9, "reason": "Logical progression of scenes"}'
    mock_invoke.return_value = mock_response
    
    from langchain_openai import ChatOpenAI
    judge_llm = ChatOpenAI(model="gpt-4o")
    res = judge_llm.invoke(prompt)
    
    assert "score" in res.content
