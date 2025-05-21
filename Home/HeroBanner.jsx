import React, { useEffect, useState } from "react";

export default function HeroBanner() {
  const [changeText, setChangeText] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setChangeText((prev) => {
        return prev === 2 ? 0 : prev + 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);
  return (
    <section
      className="bg-cover bg-center bg-no-repeat w-full h-auto"
      style={{ backgroundImage: "url('/home/sec1/banner-bg.png')" }}
    >
      <div className="bg-[#0000000f]">
        <div className="marquee-container">
          <div className="marquee-content">
            <span className="marquee-text">
              Hey! It looks like you are from USA. We support Purchasing Power
              Parity pricing, so enjoy 50% off on your subscription. Use code:
              abc589
            </span>
            <span className="marquee-text">
              Hey! It looks like you are from USA. We support Purchasing Power
              Parity pricing, so enjoy 50% off on your subscription. Use code:
              abc589
            </span>
          </div>
        </div>

        <div className="max-[1000px]:flex-col w-full min-h-screen flex justify-center items-center gap-10 px-[5%] py-[30px]">
          <div className="max-w-[700px] min-h-[304px] flex flex-col justify-center gap-10 items-start">
            <h3 className="max-w-[700px] w-full text-5xl font-semibold leading-[100%] text-white max-[500px]:text-4xl">
              Design Your{" "}
              <span className="text-[#ffd56b]">
                {["Interiors", "Kitchen", "Balcony", "Living Room"][changeText]}
              </span>
              <br />
              Space With AI
            </h3>
            <p
              className="max-w-[524px] w-full min-h-[30px] text-[17px] font-medium leading-[150%] text-neutral-100 max-[500px]:text-sm"
              style={{ wordSpacing: "3px" }}
            >
              Easy to Use, Zero Learning, AI Powered Design Tool to generate
              Your Own Space Photo-like images in 25 Seconds
            </p>

            <div className="max-w-[305px] w-full h-[50px] flex justify-center items-center bg-[#007b82] text-white shadow-[10px_10px_10px_10px_#2a2a2a29] cursor-pointer rounded-[5px] hover:bg-[#2e9ea4] hover:text-white max-[500px]:h-10">
              <p
                className="text-lg font-bold leading-[100%] text-center text-white"
                style={{ wordSpacing: "2px" }}
              >
                Design Now!
              </p>
            </div>
          </div>
          <div className="relative w-full max-w-[500px] min-h-[312px] group overflow-hidden rounded-lg">
            <div
              className="bg-center group-hover:opacity-0 bg-no-repeat bg-cover w-full h-full min-h-[312px] transition-opacity duration-500"
              style={{ backgroundImage: "url('/home/sec1/banner-home.png')" }}
            >
              <div className="flex flex-col justify-start items-start gap-[5px] pl-[25px] pt-2.5 max-[500px]:p-3">
                <div className="max-w-[149px] w-full h-[34px] rounded bg-[#00000066] flex justify-center items-center gap-2.5 px-2.5 py-1.5">
                  <p className="max-w-[129px] w-full text-base font-medium leading-[100%] text-white z-[1]">
                    ORGINAL ROOM
                  </p>
                </div>
                <p className="max-w-[44px] w-full h-5 text-sm leading-[100%] font-medium text-white z-[1] pl-[5px]">
                  Before
                </p>
              </div>
            </div>

            <div
              className="absolute top-0 left-0 bg-center bg-no-repeat bg-cover w-full h-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 min-h-[312px]"
              style={{ backgroundImage: "url('/home/sec1/afterImg.png')" }}
            >
              <div className="flex flex-col justify-start items-start gap-[5px] pl-[25px] pt-2.5 max-[500px]:p-3">
                <div className="max-w-[149px] w-full h-[34px] rounded bg-[#00000066] flex justify-center items-center gap-2.5 px-2.5 py-1.5">
                  <p className="max-w-[129px] w-full text-base font-medium leading-[100%] text-white z-[1]">
                    STACKLYAI
                  </p>
                </div>
                <p className="max-w-[44px] w-full h-5 text-sm leading-[100%] font-medium text-white z-[1] pl-[5px]">
                  After
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
