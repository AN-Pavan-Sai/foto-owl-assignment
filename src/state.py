import operator
from typing import TypedDict, Annotated, List, Optional, Any
from src.models import VideoIntent, Storyboard, ImageAnalysis

class GraphState(TypedDict):
    """
    Represents the state of our video generation pipeline.
    """
    user_prompt: str
    image_paths: List[str]
    
    intent: Optional[VideoIntent]
    image_analyses: List[ImageAnalysis]
    
    storyboard: Optional[Storyboard]
    remotion_script: Optional[str]
    
    compile_error: Optional[str]
    retry_count: int
    
    render_success: bool
    final_video_path: Optional[str]
