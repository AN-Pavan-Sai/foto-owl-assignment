import { Sequence, Img, staticFile } from "remotion";

export const MyVideo: React.FC<any> = () => {
  return (
    <>
      <Sequence from={0} durationInFrames={30}>
        <Img src={staticFile("sample_images/image_0.jpg")} style={{ width: '100%', height: '100%' }} />
      </Sequence>
      <Sequence from={30} durationInFrames={30}>
        <Img src={staticFile("sample_images/image_1.jpg")} style={{ width: '100%', height: '100%' }} />
      </Sequence>
      <Sequence from={60} durationInFrames={30}>
        <Img src={staticFile("sample_images/image_2.jpg")} style={{ width: '100%', height: '100%' }} />
      </Sequence>
      <Sequence from={90} durationInFrames={30}>
        <Img src={staticFile("sample_images/image_3.jpg")} style={{ width: '100%', height: '100%' }} />
      </Sequence>
      <Sequence from={120} durationInFrames={30}>
        <Img src={staticFile("sample_images/image_4.jpg")} style={{ width: '100%', height: '100%' }} />
      </Sequence>
    </>
  );
};