import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.graph import build_graph

def main():
    if not os.getenv("GROQ_API_KEY"):
        print("Please set GROQ_API_KEY in your .env file.")
        return

    # Sample prompt and images
    user_prompt = "Cinematic wedding reel, slow and emotional, warm tones, minimal text"
    
    # We simulate reading from a folder
    image_dir = "remotion/public/sample_images"
    os.makedirs(image_dir, exist_ok=True)
    # create dummy images if none exist
    if not os.listdir(image_dir):
        from PIL import Image
        for i in range(5):
            img = Image.new('RGB', (1920, 1080), color=(73, 109, 137))
            img.save(os.path.join(image_dir, f"image_{i}.jpg"))
            
    image_paths = [f"sample_images/{f}" for f in os.listdir(image_dir) if f.endswith(".jpg")]
    
    print(f"Running pipeline with {len(image_paths)} images...")
    
    app = build_graph()
    
    inputs = {
        "user_prompt": user_prompt,
        "image_paths": image_paths,
        "retry_count": 0
    }
    
    # Run the graph
    config = {"recursion_limit": 15}
    final_state = app.invoke(inputs, config=config)
    
    print("\n--- Pipeline Completed ---")
    print(f"Render Success: {final_state.get('render_success')}")
    if final_state.get('render_success'):
        print(f"Video saved to: {final_state.get('final_video_path')}")
        
    # Save trace and storyboard
    os.makedirs("sample_output", exist_ok=True)
    
    if final_state.get("storyboard"):
        with open("sample_output/storyboard.json", "w") as f:
            f.write(final_state["storyboard"].model_dump_json(indent=2))
            
    if final_state.get("remotion_script"):
        with open("sample_output/script.tsx", "w") as f:
            f.write(final_state["remotion_script"])
            
    # Save the trace excluding the actual prompt/api key if any
    trace_state = {k: v for k, v in final_state.items() if k not in ["image_paths", "storyboard"]}
    trace_state["storyboard_generated"] = final_state.get("storyboard") is not None
    
    # Simple dict serialization for trace
    with open("sample_output/trace.json", "w") as f:
        # Convert Pydantic models to dict for serialization
        if "intent" in trace_state and trace_state["intent"]:
            trace_state["intent"] = trace_state["intent"].model_dump()
        if "image_analyses" in trace_state:
            trace_state["image_analyses"] = [a.model_dump() for a in trace_state["image_analyses"]]
            
        json.dump(trace_state, f, indent=2)
        
    print("Output saved to sample_output/ directory.")

if __name__ == "__main__":
    main()
