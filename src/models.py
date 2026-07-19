from pydantic import BaseModel, Field
from typing import List, Optional

class VideoIntent(BaseModel):
    pacing: str = Field(description="The pacing of the video, e.g., 'slow and emotional', 'fast and energetic', 'medium'")
    visual_style: str = Field(description="The visual style or color grading, e.g., 'warm tones', 'cinematic', 'corporate'")
    caption_tone: str = Field(description="The tone of the captions, e.g., 'minimal text', 'bold', 'professional'")
    transition_preference: str = Field(description="The preferred type of transitions, e.g., 'subtle fades', 'fast cuts', 'wipes'")

class Scene(BaseModel):
    image_path: str = Field(description="The relative or absolute path to the selected image")
    duration_frames: int = Field(description="The duration of this scene in frames (assuming 30fps, 30 = 1 second)")
    caption: str = Field(description="The text caption to display on this scene")
    transition_type: str = Field(description="The type of transition to use when entering this scene, e.g., 'fade', 'cut'")
    animation_style: str = Field(description="The animation to apply to the image, e.g., 'zoom-in', 'pan-right', 'none'")

class Storyboard(BaseModel):
    scenes: List[Scene] = Field(description="The sequence of scenes in the video")
    total_duration_frames: int = Field(description="The total duration of the video in frames")

class ImageAnalysis(BaseModel):
    image_path: str = Field(description="Path to the image")
    description: str = Field(description="Visual description of the image content")
    quality_score: int = Field(description="Estimated quality or relevance score from 1-10")
