import { Composition, registerRoot } from "remotion";
import { MyVideo } from "./MyVideo";

const storyboardData = {"scenes":[{"image_path":"sample_images/image_0.jpg","duration_frames":30,"caption":"","transition_type":"fade","animation_style":"none"},{"image_path":"sample_images/image_1.jpg","duration_frames":30,"caption":"","transition_type":"fade","animation_style":"none"},{"image_path":"sample_images/image_2.jpg","duration_frames":30,"caption":"","transition_type":"fade","animation_style":"none"},{"image_path":"sample_images/image_3.jpg","duration_frames":30,"caption":"","transition_type":"fade","animation_style":"none"},{"image_path":"sample_images/image_4.jpg","duration_frames":30,"caption":"","transition_type":"fade","animation_style":"none"}],"total_duration_frames":150};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MyVideo"
        component={MyVideo}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ storyboard: storyboardData }}
      />
    </>
  );
};

registerRoot(RemotionRoot);
