import os
import subprocess
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.state import GraphState
from src.models import VideoIntent, Storyboard, ImageAnalysis
from src.rag import RAGSystem

# Initialize LLMs (Using llama-3.1-8b-instant for cheap tasks, llama-3.3-70b-versatile for complex tasks)
llm_mini = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
llm_pro = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)

def intent_parser_node(state: GraphState) -> dict:
    """Parses user prompt into VideoIntent"""
    print("--- Intent Parser ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert video producer. Parse the user's creative brief into a structured VideoIntent object."),
        ("user", "{user_prompt}")
    ])
    
    chain = prompt | llm_mini.with_structured_output(VideoIntent)
    intent = chain.invoke({"user_prompt": state["user_prompt"]})
    return {"intent": intent}

def image_analyser_node(state: GraphState) -> dict:
    """Analyzes images using vision model. (Mocked for now since passing actual images to vision model can be complex without actual files)"""
    print("--- Image Analyser ---")
    image_analyses = []
    # In a real scenario, we'd use GPT-4o with image URLs/base64.
    # Here we simulate the analysis for the provided image paths.
    for i, path in enumerate(state.get("image_paths", [])):
        # Mock analysis
        image_analyses.append(ImageAnalysis(
            image_path=path,
            description=f"A highly detailed photograph showing people at an event. Image index {i}.",
            quality_score=8
        ))
    return {"image_analyses": image_analyses}

def storyboard_writer_node(state: GraphState) -> dict:
    """Generates a storyboard based on intent and image analyses, using RAG for style guidelines."""
    print("--- Storyboard Writer ---")
    intent = state["intent"]
    
    # Retrieve style context
    rag = RAGSystem()
    style_retriever = rag.get_style_retriever()
    style_docs = style_retriever.invoke(intent.visual_style)
    style_context = "\n\n".join([doc.page_content for doc in style_docs])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a storyboard director. Create a video storyboard.\n\nStyle Context:\n{style_context}\n\nVideo Intent:\nPacing: {pacing}\nCaption Tone: {caption_tone}\nTransition Preference: {transitions}"),
        ("user", "Available Images and Analysis:\n{image_analyses}\n\nPlease generate a structured Storyboard selecting the best images and arranging them logically. Total duration should be appropriate for the pacing.")
    ])
    
    chain = prompt | llm_pro.with_structured_output(Storyboard)
    analyses_str = "\n".join([f"- {a.image_path}: {a.description} (Quality: {a.quality_score})" for a in state["image_analyses"]])
    
    storyboard = chain.invoke({
        "style_context": style_context,
        "pacing": intent.pacing,
        "caption_tone": intent.caption_tone,
        "transitions": intent.transition_preference,
        "image_analyses": analyses_str
    })
    
    return {"storyboard": storyboard}

def script_generator_node(state: GraphState) -> dict:
    """Generates the Remotion TSX script based on storyboard, using RAG for API context."""
    print("--- Script Generator ---")
    storyboard = state["storyboard"]
    compile_error = state.get("compile_error", "")
    
    rag = RAGSystem()
    api_retriever = rag.get_api_retriever()
    
    query = "Remotion Composition Sequence Img interpolate"
    if compile_error:
        query = f"Fix error: {compile_error}"
    
    api_docs = api_retriever.invoke(query)
    api_context = "\n\n".join([doc.page_content for doc in api_docs])
    
    sys_prompt = "You are an expert React and Remotion developer. Write a complete, valid Remotion composition script in TSX."
    if compile_error:
        sys_prompt += "\n\nTHE PREVIOUS SCRIPT FAILED TO COMPILE. ERROR:\n{compile_error}\n\nFix the error in the new script."
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_prompt + "\n\nRemotion API Reference:\n{api_context}"),
        ("user", "Storyboard:\n{storyboard_json}\n\nOutput only raw TSX code. Do not use markdown blocks. Import everything necessary from 'remotion'. The component should be exported as 'MyVideo'.\nNOTE: Avoid unused variables/imports. Use 'durationInFrames' for Remotion Sequence components, not 'duration'. Do NOT generate `RemotionRoot` or `<Composition>`. Type `MyVideo` as `React.FC<any>` to avoid LooseComponentType errors. Use `Img` from 'remotion' for images and pass `staticFile(scene.image_path)` to its `src` prop (import `staticFile` from 'remotion').")
    ])
    
    chain = prompt | llm_pro
    response = chain.invoke({
        "api_context": api_context,
        "storyboard_json": storyboard.model_dump_json(),
        "compile_error": compile_error if compile_error else ""
    })
    
    script_content = response.content
    # Clean up if the LLM adds markdown blocks despite instructions
    if script_content.startswith("```tsx"):
        script_content = script_content.replace("```tsx", "").replace("```", "").strip()
        
    return {"remotion_script": script_content}

def compiler_fixer_node(state: GraphState) -> dict:
    """Compiles the Remotion script, catches errors."""
    print("--- Compiler & Fixer ---")
    script = state["remotion_script"]
    retry_count = state.get("retry_count", 0)
    storyboard_json = state["storyboard"].model_dump_json() if state.get("storyboard") else "{}"
    
    # Write the script to the Remotion project
    script_path = os.path.join("remotion", "src", "MyVideo.tsx")
    with open(script_path, "w") as f:
        f.write(script)
        
    # We also need a Root component to register MyVideo. We'll assume it exists or write a minimal one.
    root_path = os.path.join("remotion", "src", "Root.tsx")
    if not os.path.exists(root_path) or True: # always overwrite for simplicity
        with open(root_path, "w") as f:
            f.write(f'''import {{ Composition, registerRoot }} from "remotion";
import {{ MyVideo }} from "./MyVideo";

const storyboardData = {storyboard_json};

export const RemotionRoot: React.FC = () => {{
  return (
    <>
      <Composition
        id="MyVideo"
        component={{MyVideo}}
        durationInFrames={{300}}
        fps={{30}}
        width={{1920}}
        height={{1080}}
        defaultProps={{{{ storyboard: storyboardData }}}}
      />
    </>
  );
}};

registerRoot(RemotionRoot);
''')

    # Run the Remotion build command to check for compile errors
    try:
        # Note: Remotion doesn't have a strict 'compile only' command without rendering, 
        # but we can try running `tsc` or `npx eslint` or trigger a small render.
        # We will use `npx tsc --noEmit` to check for TS errors.
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            cwd="remotion",
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            error_msg = result.stdout + "\n" + result.stderr
            return {"compile_error": error_msg, "retry_count": retry_count + 1, "render_success": False}
        else:
            return {"compile_error": None, "retry_count": retry_count, "render_success": True}
            
    except Exception as e:
        return {"compile_error": str(e), "retry_count": retry_count + 1, "render_success": False}

def renderer_node(state: GraphState) -> dict:
    """Triggers final video render."""
    print("--- Renderer ---")
    # Actually render the video
    try:
        result = subprocess.run(
            ["npx", "remotion", "render", "src/Root.tsx", "MyVideo", "../output/final_video.mp4"],
            cwd="remotion",
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return {"render_success": True, "final_video_path": "output/final_video.mp4"}
        else:
            print("Render failed:", result.stderr)
            return {"render_success": False}
    except Exception as e:
        print("Render failed with exception:", e)
        return {"render_success": False}
