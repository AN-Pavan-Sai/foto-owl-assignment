# Remotion Composition
```tsx
import { Composition } from "remotion";
import { MyVideo } from "./MyVideo";

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
        defaultProps={{ storyboard: [] }}
      />
    </>
  );
};
```

# Using Img component
```tsx
import { Img } from "remotion";

export const MyImage: React.FC<{ src: string }> = ({ src }) => {
  return <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />;
};
```

# Sequence for Timeline
```tsx
import { Sequence } from "remotion";

export const MySequence: React.FC = () => {
  return (
    <>
      <Sequence from={0} durationInFrames={90}>
        <div>Scene 1</div>
      </Sequence>
      <Sequence from={90} durationInFrames={90}>
        <div>Scene 2</div>
      </Sequence>
    </>
  );
};
```

# Animations with interpolate
```tsx
import { interpolate, useCurrentFrame } from "remotion";

export const AnimatedComponent: React.FC = () => {
  const frame = useCurrentFrame();
  
  // Scale from 1 to 1.2 over 90 frames (Zoom In)
  const scale = interpolate(frame, [0, 90], [1, 1.2], {
    extrapolateRight: "clamp",
  });
  
  return <div style={{ transform: `scale(${scale})` }}>Content</div>;
};
```
