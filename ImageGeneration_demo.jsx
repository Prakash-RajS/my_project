//ImageGeneration.jsx result page
import React, { useState, useEffect } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { PacmanLoader } from "react-spinners";
import Interior from "../../assets/product-pg/Vector.png";
import Home from "../../assets/product-pg/home.png";
import Tree from "../../assets/product-pg/tree.png";
import SideArrow from "../../assets/pricing-pg/sideArrow.png";
import Report from "../../assets/product-pg/report.png";
import More from "../../assets/product-pg/more.png";
import Download from "../../assets/product-pg/do.png";
import Share from "../../assets/product-pg/share.png";
import Split from "../../assets/product-pg/split.png";

export default function ImageGeneration() {
  const location = useLocation();
  const navigate = useNavigate();

  const [originalImage, setOriginalImage] = useState(null);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [selectedStyle, setSelectedStyle] = useState("interior");
  const [buildingType, setBuildingType] = useState("residential");
  const [roomType, setRoomType] = useState("living room");
  const [roomStyle, setRoomStyle] = useState("modern");
  const [numDesigns, setNumDesigns] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [showMoreOptions, setShowMoreOptions] = useState(false);
  const [currentView, setCurrentView] = useState("split"); // 'split' or 'slide'
  const [error, setError] = useState(null);

  const backendBaseUrl = "http://localhost:8000";

  useEffect(() => {
    if (location.state) {
      // Handle both URL strings and File objects
      if (location.state.originalImage) {
        if (typeof location.state.originalImage === 'string') {
          setOriginalImage(location.state.originalImage);
        } else {
          // If it's a File object, create a URL
          setOriginalImage(URL.createObjectURL(location.state.originalImage));
        }
      }

      if (location.state.generatedImages) {
        const processedImages = location.state.generatedImages.map(img => {
          if (typeof img === 'string') {
            return { url: img, id: Date.now() + Math.random() };
          } else if (img instanceof Blob) {
            return { url: URL.createObjectURL(img), id: Date.now() + Math.random() };
          }
          return img;
        });
        setGeneratedImages(processedImages);
      }
    }
  }, [location]);

  // Clean up object URLs
  useEffect(() => {
    return () => {
      if (originalImage && originalImage.startsWith('blob:')) {
        URL.revokeObjectURL(originalImage);
      }
      generatedImages.forEach(img => {
        if (img.url && img.url.startsWith('blob:')) {
          URL.revokeObjectURL(img.url);
        }
      });
    };
  }, [originalImage, generatedImages]);

  const handleGenerateDesigns = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Replace with actual API call if needed for re-generation
      setTimeout(() => {
        const newDesigns = Array.from({ length: numDesigns }, (_, i) => ({
          id: Date.now() + i,
          url: `https://example.com/generated-image-${i}.jpg`,
          style: selectedStyle,
          timestamp: new Date().toISOString(),
        }));
        setGeneratedImages([...generatedImages, ...newDesigns]);
        setIsLoading(false);
      }, 2000);
    } catch (err) {
      console.error("Generation error:", err);
      setError("Failed to generate designs. Please try again.");
      setIsLoading(false);
    }
  };

  const handleDownload = (imageUrl) => {
    if (!imageUrl) return;
    const link = document.createElement("a");
    link.href = imageUrl;
    link.download = `design-${Date.now()}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleShare = (imageUrl) => {
    if (navigator.share) {
      navigator
        .share({
          title: "Check out my design!",
          text: "I created this using our awesome design tool",
          url: imageUrl,
        })
        .catch((err) => console.error("Error sharing:", err));
    } else {
      prompt("Copy this link to share:", imageUrl);
    }
  };

  const handleReport = (imageId) => {
    const reason = prompt("Please enter the reason for reporting:");
    if (reason) {
      alert("Thank you for your report. We'll review this design.");
    }
  };


  return (
    <div>
      <section className="w-full h-[1340px] flex justify-center items-center bg-[#002628]">
        <div className="w-[1280px] h-[1199px]">
          <div className="w-[1280px] h-[287px] rounded-tl-[20px] rounded-tr-[20px] bg-gradient-to-t from-[#002628] to-[#00646A] via-[#00B0BA] flex flex-col justify-center items-center gap-4">
            <div className="w-[658px] h-[53px] font-bold text-[38px] leading-[140%] tracking-[20px] text-center text-white">
              PICK YOUR STYLE
            </div>
            <div className="w-[658px] h-[121px] flex justify-between items-center">
              {/* Style Selection Buttons */}
              {["interior", "exteriors", "outdoors"].map((style) => (
                <div
                  key={style}
                  className="w-[101px] h-[121px] flex flex-col justify-center items-center gap-[20px] cursor-pointer"
                  onClick={() => setSelectedStyle(style)}
                >
                  <div
                    className={`w-[70px] h-[70px] rounded-[90px] ${selectedStyle === style
                      ? "bg-gradient-to-l from-[#00B0BA] via-[black] to-[#007B82] border-[2px] border-solid border-white"
                      : "bg-[#FFFFFF1A]"
                      } drop-shadow-[0_2px_4px_0 #00B0BA4D] flex justify-center items-center`}
                  >
                    <img
                      src={
                        style === "interior"
                          ? Interior
                          : style === "exteriors"
                            ? Home
                            : Tree
                      }
                      alt={style}
                    />
                  </div>
                  <div className="w-[101px] h-[31px] font-semibold text-[22px] leading-[140%] text-center text-white">
                    {style.charAt(0).toUpperCase() + style.slice(1)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Main Content Area */}
          <div className="w-[1280px] h-[912px] rounded-bl-[20px] rounded-br-[20px] bg-[white] drop-shadow-[0_1px_4px_0 #00000059] p-[20px]">
            <div className="w-[1240px] h-[868px] rounded-[6px] flex flex-col justify-start items-start gap-[30px]">
              {/* Navigation Controls */}
              <div className="w-[100%] h-[30px] flex justify-between">
                <Link to="/">
                  <div className="w-[75px] flex justify-center items-center cursor-pointer">
                    <img
                      src={SideArrow}
                      alt="Back"
                      className="w-[24px] h-[24px]"
                    />
                    <div className="font-medium text-[16px] leading-[156%] text-[#2A2A2A]">
                      Back
                    </div>
                  </div>
                </Link>

                <div className="w-[350px] h-[25px] flex justify-center items-center gap-[32px]">
                  <div
                    className="w-[105px] flex justify-center items-center gap-1 cursor-pointer"
                    onClick={() => handleDownload(designs[0]?.id)}
                  >
                    <img
                      src={Download}
                      alt="Download"
                      className="w-[24px] h-[24px]"
                    />
                    <div className="font-medium text-[16px] leading-[156%] text-[#2A2A2A]">
                      Download
                    </div>
                  </div>
                  <div
                    className="w-[73px] flex justify-center items-center gap-1 cursor-pointer"
                    onClick={() => handleShare(designs[0]?.id)}
                  >
                    <img
                      src={Share}
                      alt="Share"
                      className="w-[24px] h-[24px]"
                    />
                    <div className="font-medium text-[16px] leading-[156%] text-[#2A2A2A]">
                      Share
                    </div>
                  </div>
                  <div
                    className="w-[80px] flex justify-center items-center gap-1 cursor-pointer"
                    onClick={() => handleReport(designs[0]?.id)}
                  >
                    <img
                      src={Report}
                      alt="Report"
                      className="w-[24px] h-[24px]"
                    />
                    <div className="font-medium text-[16px] leading-[156%] text-[#2A2A2A]">
                      Report
                    </div>
                  </div>
                  <div
                    className="w-[75px] flex justify-center items-center gap-1 cursor-pointer"
                    onClick={() => setShowMoreOptions(!showMoreOptions)}
                  >
                    <img
                      src={More}
                      alt="More options"
                      className="w-[24px] h-[24px]"
                    />
                  </div>
                </div>
              </div>

              {/* More Options Dropdown */}
              {showMoreOptions && (
                <div className="absolute right-[40px] top-[340px] bg-white shadow-lg rounded-md p-2 z-10">
                  <div className="py-1 cursor-pointer hover:bg-gray-100 px-3">
                    Save to favorites
                  </div>
                  <div className="py-1 cursor-pointer hover:bg-gray-100 px-3">
                    Duplicate design
                  </div>
                  <div className="py-1 cursor-pointer hover:bg-gray-100 px-3">
                    Delete design
                  </div>
                </div>
              )}

              {/* Form Controls */}
              <div className="w-[1177px] h-[74px] flex justify-between items-center">
                <div className="w-[268px] h-[74px] flex flex-col justify-start items-start gap-[10px]">
                  <div className="w-[100%] h-[22px] font-[400] text-[16px] leading-[140%] text-[#2A2A2A]">
                    Building Type
                  </div>
                  <div className="w-[268px] h-[42px] rounded-[4px] border-[1px] border-solid border-[#00B0BA] flex justify-center items-center p-[10px]">
                    <select
                      value={buildingType}
                      onChange={(e) => setBuildingType(e.target.value)}
                      className="w-[100%] outline-none"
                    >
                      <option value="residential">Residential</option>
                      <option value="commercial">Commercial</option>
                      <option value="industrial">Industrial</option>
                    </select>
                  </div>
                </div>
                <div className="w-[268px] h-[74px] flex flex-col justify-start items-start gap-[10px]">
                  <div className="w-[100%] h-[22px] font-[400] text-[16px] leading-[140%] text-[#2A2A2A]">
                    Room Type
                  </div>
                  <div className="w-[268px] h-[42px] rounded-[4px] border-[1px] border-solid border-[#00B0BA] flex justify-center items-center p-[10px]">
                    <select
                      value={roomType}
                      onChange={(e) => setRoomType(e.target.value)}
                      className="w-[100%] outline-none"
                    >
                      <option value="living room">Living Room</option>
                      <option value="bedroom">Bedroom</option>
                      <option value="kitchen">Kitchen</option>
                      <option value="bathroom">Bathroom</option>
                    </select>
                  </div>
                </div>
                <div className="w-[268px] h-[74px] flex flex-col justify-start items-start gap-[10px]">
                  <div className="w-[100%] h-[22px] font-[400] text-[16px] leading-[140%] text-[#2A2A2A]">
                    Room Style
                  </div>
                  <div className="w-[268px] h-[42px] rounded-[4px] border-[1px] border-solid border-[#00B0BA] flex justify-center items-center p-[10px]">
                    <select
                      value={roomStyle}
                      onChange={(e) => setRoomStyle(e.target.value)}
                      className="w-[100%] outline-none"
                    >
                      <option value="modern">Modern</option>
                      <option value="traditional">Traditional</option>
                      <option value="minimalist">Minimalist</option>
                      <option value="industrial">Industrial</option>
                    </select>
                  </div>
                </div>
                <div className="w-[268px] h-[74px] flex flex-col justify-start items-start gap-[10px]">
                  <div className="w-[100%] h-[22px] font-[400] text-[16px] leading-[140%] text-[#2A2A2A]">
                    Number Of Designs
                  </div>
                  <div className="w-[268px] h-[42px] rounded-[4px] border-[1px] border-solid border-[#00B0BA] flex justify-center items-center p-[10px]">
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={numDesigns}
                      onChange={(e) => setNumDesigns(e.target.value)}
                      className="w-[100%] outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Image Display */}
              <div className="w-[1176px] h-[360px] flex flex-col gap-[10px] p-[20px]">
                <div className="w-[100%] h-[24px] flex justify-end">
                  <div
                    className="w-[180px] flex justify-center items-center gap-1 cursor-pointer"
                    onClick={() =>
                      setCurrentView(
                        currentView === "split" ? "slide" : "split"
                      )
                    }
                  >
                    <img
                      src={Split}
                      alt="Toggle view"
                      className="w-[24px] h-[24px]"
                    />
                    <div className="font-medium text-[18px] leading-[156%] text-[#2A2A2A]">
                      {currentView === "split" ? "Slide view" : "Split view"}
                    </div>
                  </div>
                </div>

                {currentView === "split" ? (
                  <div className="w-[100%] h-[336px] flex justify-between items-center gap-4">
                    <div>
                      {originalImage && (
                        <img
                          src={originalImage}
                          alt="Original design"
                          className="max-h-[336px]"
                        />
                      )}
                    </div>
                    <div>
                      {generatedImages.length > 0 && (
                        <img
                          src={generatedImages[0].url}
                          alt="Generated design"
                          className="max-h-[336px]"
                        />
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="w-[100%] h-[336px] overflow-x-auto flex gap-4">
                    {designs.map((design) => (
                      <div key={design.id} className="flex-shrink-0">
                        <img
                          src={design.after}
                          alt={`Generated design ${design.id}`}
                          className="h-[336px]"
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Create More Designs Button */}
              <div className="w-[100%] h-[55px] flex justify-center items-center mt-[50px]">
                <button
                  onClick={handleGenerateDesigns}
                  disabled={isLoading}
                  className={`w-[193px] h-[54px] flex justify-center items-center border-[1px] border-solid border-[#00B0BA] font-semibold text-[18px] rounded-[10px] text-[#2A2A2A] ${isLoading
                    ? "opacity-50 cursor-not-allowed"
                    : "hover:bg-[#00B0BA20]"
                    }`}
                >
                  {isLoading ? "Generating..." : "Create More Designs"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}



