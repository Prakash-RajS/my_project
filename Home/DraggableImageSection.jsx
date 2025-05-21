import React from "react";

import dragImg1_1 from "../../assets/home/draggableImgSection/drag1(1).png";
import dragImg1_2 from "../../assets/home/draggableImgSection/drag1(2).png";
import dragImg2_1 from "../../assets/home/draggableImgSection/drag2(1).png";
import dragImg2_2 from "../../assets/home/draggableImgSection/drag2(2).png";
import dragImg3_1 from "../../assets/home/draggableImgSection/drag3(1).png";
import dragImg3_2 from "../../assets/home/draggableImgSection/drag3(2).png";
import DraggableImages from "../../components/DraggableImages";

export default function DraggableImageSection() {
  return (
    <section className="w-full bg-[#011213] text-white py-16 px-4 flex flex-col items-center">
      {/* Heading */}
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-semibold leading-tight">
          {" "}
          <span className="text-cyan-400"></span>
        </h2>
        <h2 className="text-3xl md:text-5xl font-semibold leading-tight mt-2"></h2>
      </div>

      {/* Features Section */}
      <div className="flex flex-col gap-16 w-full max-w-7xl">
        {/* Feature 1 */}
        <div className="flex flex-col md:flex-row items-center gap-8">
          {/* Text */}
          <div className="flex-1">
            <h3 className="text-[34px] font-semibold leading-[140%] mb-4">
              <span className="text-cyan-400">Gorgeous Makeovers</span> and
              Stylish Transformations
            </h3>
            <p className="leading-[200%] text-[18px] font-medium text-[#f5f5f5]">
              Want to give your home a stunning new look inside and out? Our
              AI-powered makeover feature lets you explore various styles to
              elevate your space. Redesign any interior, exterior, or outdoor
              area effortlessly.
            </p>
          </div>
          {/* Image */}
          <div className="flex-1 max-w-[500px] min-w-[300px] w-full">
            <DraggableImages imageRight={dragImg1_1} imageLeft={dragImg1_2} />
          </div>
        </div>

        {/* Feature 2 */}
        <div className="flex flex-col md:flex-row items-center gap-8">
          {/* Text */}
          <div className="flex-1">
            <h3 className="text-[34px] font-semibold leading-[140%] mb-4">
              <span className="text-cyan-400">Transform Empty Spaces</span> with
              Stylish Furniture
            </h3>
            <p className="leading-[200%] text-[18px] font-medium text-[#f5f5f5]">
              Curious how your room would look fully furnished? Our AI-powered
              tool fills any room type with furniture and décor. Perfect for
              empty or under-construction spaces—bring your vision to life with
              Stackly.
            </p>
          </div>
          {/* Image */}
          <div className="flex-1 max-w-[500px] min-w-[300px] w-full">
            <DraggableImages imageRight={dragImg2_1} imageLeft={dragImg2_2} />
          </div>
        </div>

        {/* Feature 3 */}
        <div className="flex flex-col md:flex-row items-center gap-8">
          {/* Text */}
          <div className="flex-1">
            <h3 className="text-[34px] font-semibold leading-[140%] mb-4">
              Artistic Makeover for{" "}
              <span className="text-cyan-400">Interiors and Exteriors</span>
            </h3>
            <p className="leading-[200%] text-[18px] font-medium text-[#f5f5f5]">
              Unleash the power of AI with Artistic Makeover. From stylish
              furniture arrangements to a complete exterior refresh, let AI
              transform your space with a fresh, creative vision.
            </p>
          </div>
          {/* Image */}
          <div className="flex-1 max-w-[500px] min-w-[300px] w-full">
            <DraggableImages imageRight={dragImg3_1} imageLeft={dragImg3_2} />
          </div>
        </div>
      </div>

      {/* Bottom Text */}
      <div className="mt-16 text-center max-w-[681px] text-[#ffffff] font-normal text-[24px] leading-[180%] align-center">
        Loved by experts and designed for everyone, our platform brings
        professional-quality results with ease and simplicity.
      </div>

      {/* Call to Action */}
      <div className="mt-8 flex flex-col items-center gap-4">
        <h3 className="text-[32px] font-semibold text-[#00b0ba] leading-[140%]">
          Get Started – Infinite Ideas.
        </h3>
        <a
          href="#"
          className="max-w-[406px] min-h-[60px] rounded-[5px] hover:bg-cyan-500 text-white font-semibold py-4 px-8 rounded-md text-[20px] leading-[35px] spacing-[8px] transition"style={{
            background:
              "linear-gradient(to right, #007c82 0%,rgb(4, 68, 75),rgb(3, 89, 94) 100%)",
          }}
        >
          Access Now !
        </a>
      </div>
    </section>
  );
}
