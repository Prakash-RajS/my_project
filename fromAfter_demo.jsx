import React, { useContext, useRef, useState } from "react";
import { UserContext } from "../../context/UserContext";
import { useNavigate } from "react-router-dom";
import Interior from "../../assets/product-pg/Vector.png";
import Home from "../../assets/product-pg/home.png";
import Tree from "../../assets/product-pg/tree.png";
import Lock from "../../assets/product-pg/lock.png";
import Galley from "../../assets/product-pg/gallery.png";
import I from "../../assets/product-pg/i.png";
import Magic from "../../assets/product-pg/magic.png";
import axios from "axios"; //For connect fastapi 

export default function Form() {
  const { userInfo } = useContext(UserContext);
  const navigate = useNavigate();
  const inpRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [activeTab, setActiveTab] = useState("Interiors");
  const [imgFile, setImgFile] = useState(null);
  const [generatedImages, setGeneratedImages] = useState([]); // To store generated image URLs
  const [originalImageUrl, setOriginalImageUrl] = useState(null);



  const [formData, setFormData] = useState({
    buildingType: "",
    roomType: "",
    roomStyle: "",
    numDesigns: "1",
    aiStrength: "Low",
    houseAngle: "",
    spaceType: "",
  });

  const [imgURL, setImgURL] = useState(null);

  const tabs = [
    { name: "Interiors", icon: Interior },
    { name: "Exteriors", icon: Home },
    { name: "Outdoors", icon: Tree },
    // { name: "Upgrade to Unlock", icon: Lock },
  ];

  // Updated options for each tab
  const roomTypes = {
    Interiors: [
      "Living room",
      "Bedroom",
      "Kitchen",
      "Home office",
      "Dining room",
      "Study room",
      "Family room",
      "Kid room",
      "Balcony",
    ],
    Exteriors: [
      "Front side",
      "Back side",
      "Left side",
      "Right side",
    ],
    Outdoors: [
      "Front Yard",
      "Backyard",
      "Balcony",
      "Terrace/Rooftop",
      "Driveway/Parking Area",
      "Walkway/Path",
      "Lounge",
      "Porch",
      "Fence",
      "Garden",
    ],
  };

  const styles = {
    Interiors: [
      "classic",
      "modern",
      "minimal",
      "scandinavian",
      "contemporary",
      "industrial",
      "japandi",
      "bohemian", // Changed from "Bohemian (Boho)"
      "coastal",
      "modern luxury",
      "tropical resort",
      "japanese zen",
    ],
    Exteriors: [
      "classic",
      "modern",
      "bohemian", // Changed from "Bohemian (Boho)"
      "coastal",
      "international",
      "elephant",
      "stone clad",
      "glass house",
      "red brick",
      "painted brick",
      "wood accents",
      "industrial",
    ],
    Outdoors: [
      "modern",
      "contemporary",
      "traditional",
      "rustic",
      "scandinavian",
      "classic garden",
      "coastal outdoor",
      "farmhouse",
      "cottage garden",
      "industrial",
      "beach",
    ],
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const changeImage = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith("image/")) {
      setImgFile(file);
      const preview = URL.createObjectURL(file);
      setImgURL(preview);
    } else {
      alert("Please upload only image files.");
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      setImgFile(file);
      const preview = URL.createObjectURL(file);
      setImgURL(preview);
    } else {
      alert("Please drop only image files.");
    }
  };

  const handleChange = (value, key) => {
    setFormData((prev) => {
      return { ...prev, [key]: value };
    });
  };

  const handleTabChange = (tabName) => {
    if (tabName === "Upgrade to Unlock") {
      alert("Please upgrade your account to access this feature");
    } else {
      setActiveTab(tabName);
      // Reset relevant form fields when switching tabs
      setFormData({
        buildingType: "",
        roomType: "",
        roomStyle: "",
        numDesigns: "1",
        aiStrength: "Low",
        houseAngle: "",
        spaceType: "",
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setProgress(0);

    try {
      if (!imgFile) throw new Error("Please upload an image first!");

      const formDataToSend = new FormData();
      formDataToSend.append("image", imgFile);
      formDataToSend.append("design_style", formData.roomStyle);
      formDataToSend.append("ai_strength", formData.aiStrength); // Fixed to use aiStrength
      formDataToSend.append("num_designs", formData.numDesigns.toString());

      let endpoint = "";
      switch (activeTab) {
        case "Interiors":
          endpoint = "generate-interior-design";
          formDataToSend.append("building_type", formData.buildingType);
          formDataToSend.append("room_type", formData.roomType);
          break;
        case "Exteriors":
          endpoint = "generate-exterior-design";
          formDataToSend.append("house_angle", formData.roomType);
          break;
        case "Outdoors":
          endpoint = "generate-outdoor-design";
          formDataToSend.append("space_type", formData.roomType);
          break;
      }

      const response = await axios.post(
        `http://localhost:8000/api/${endpoint}/`,
        formDataToSend,
        {
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          },
        }
      );

      if (response.data.success) {
        navigate("/ImageGeneration", {
          state: {
            originalImage: imgURL,
            generatedImages: Array.isArray(response.data.designs) // Use 'designs' here
              ? response.data.designs.map(url => ({ // 'url' directly as the backend sends URLs
                url: url,
                id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
              }))
              : [],
            formData: {
              style: formData.roomStyle,
              type: activeTab.toLowerCase()
            }
          }
        });
      } else {
        throw new Error(response.data.message || "Design generation failed");
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.message || error.message || "Failed to connect to server";
      alert(`Error: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="w-full min-h-screen pb-[50px] px-6 sm:px-10 py-10 flex flex-col justify-start items-center gap-y-10 bg-gradient-to-l from-[#002628] to-[#00646A] overflow-hidden">
      {/* Header */}
      <div className="w-full max-w-4xl text-center space-y-2">
        <h1 className="text-[clamp(2rem,5vw,3rem)] font-semibold text-white leading-snug">
          Let AI Style It
        </h1>
        <p className="text-[clamp(1rem,2.5vw,1.5rem)] font-medium text-white leading-snug">
          Upload a photo to begin your AI-powered {activeTab.toLowerCase()}{" "}
          design
        </p>
      </div>

      {/* Tabs */}
      <div className="w-full max-w-6xl flex flex-wrap justify-center items-center gap-4">
        {tabs.map((tab) => (
          <div
            key={tab.name}
            className="w-[clamp(120px,15vw,200px)] max-w-[200px] h-[clamp(100px,12vh,128px)] flex flex-col justify-center items-center gap-2 cursor-pointer"
            onClick={() => handleTabChange(tab.name)}
          >
            <div
              className={`w-[clamp(60px,6vw,77px)] aspect-square border-2 p-2 flex justify-center items-center rounded-full transition-all duration-200 ${activeTab === tab.name
                ? "border-white bg-gradient-to-l from-[#00B0BA] via-[#000000] to-[#007B82]"
                : "border-[#FFFFFF1A] bg-[#FFFFFF1A] hover:border-blue-300"
                }`}
            >
              <img
                src={tab.icon}
                alt={tab.name}
                className="w-full h-auto max-w-[60%] max-h-[60%] object-contain"
              />
            </div>
            <p className="text-white text-[clamp(0.9rem,1.5vw,1.4rem)] font-semibold text-center">
              {tab.name}
            </p>
          </div>
        ))}
      </div>


      {/* Form Section */}
      <div className="w-full max-w-7xl flex flex-col xl:flex-row gap-10 items-start justify-between">
        {/* Upload */}
        <div className="w-full xl:w-1/2 max-w-xl flex flex-col items-center gap-4">
          <div
            className="w-full aspect-[4/3] max-h-[70vh] border-2 border-dashed border-white rounded-xl flex justify-center items-center cursor-pointer"
            onClick={() => inpRef.current.click()}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            {imgURL ? (
              <img
                src={imgURL}
                alt="Preview"
                className="w-full h-full object-cover rounded-xl"
              />
            ) : (
              <div className="w-[clamp(180px,25vw,280px)] flex flex-col items-center gap-2">
                <div className="w-[clamp(40px,5vw,70px)] aspect-square rounded-full p-2 bg-[#FFFFFF1A] flex justify-center items-center">
                  <img src={Galley} alt="gallery" className="w-full h-auto" />
                </div>
                <p className="text-[#FFFFFFB2] text-center text-[clamp(0.9rem,2vw,1.5rem)] leading-snug">
                  Drag & drop or click to upload a photo
                </p>
              </div>
            )}
            <input
              type="file"
              name="image"
              ref={inpRef}
              onChange={changeImage}
              accept="image/*"
              className="hidden"
            />
          </div>

          <div className="w-[147px] h-[40px] rounded-[6px] border-[1.5px] border-solid border-white px-[10px] py-[8px] flex justify-around items-center cursor-pointer">
            <div className="w-[24px] h-[24px]">
              <img src={I} alt="i" />
            </div>
            <div className="w-[93px] h-[19px] text-[16px] font-[medium] leading-[100%] text-center text-white">
              Photo guide
            </div>
          </div>
        </div>

        {/* Form Controls */}
        <form
          onSubmit={handleSubmit}
          className="w-full xl:w-1/2 max-w-xl flex flex-col gap-6"
        >
          {/* Building Type (only for Interior) */}
          {activeTab === "Interiors" && (
            <div className="space-y-2">
              <label className="text-white text-lg">Choose Building Type</label>
              <div className="flex flex-col sm:flex-row gap-4">
                {["Commercial", "Residential"].map((type) => (
                  <div
                    key={type}
                    className={`flex-1 flex justify-between items-center px-4 py-2 rounded-md cursor-pointer ${formData.buildingType === type.toLowerCase() // Changed here
                      ? "bg-white text-[#007B82]"
                      : "bg-[#00000033] text-[#FFFFFF80]"
                      }`}
                    onClick={() => handleChange(type.toLowerCase(), "buildingType")} // Changed here
                  >
                    <span>{type}</span>
                    <input
                      type="radio"
                      checked={formData.buildingType === type.toLowerCase()} // Changed here
                      onChange={() => { }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Room Type (dynamic label based on tab) */}
          <div className="space-y-2">
            <label className="text-white text-lg">
              {activeTab === "Interiors"
                ? "Select Room Type"
                : activeTab === "Exteriors"
                  ? "Select House Angle"
                  : "Select Space"}
            </label>
            <select
              name="roomType"
              value={formData.roomType}
              onChange={(e) => handleChange(e.target.value.toLowerCase(), "roomType")}
              className="w-full p-3 rounded-md bg-white text-[#007B82] cursor-pointer"
              required
            >
              <option value="">Select an option</option>
              {roomTypes[activeTab].map((room) => (
                <option key={room} value={room.toLowerCase()}>
                  {room}
                </option>
              ))}
            </select>
          </div>

          {/* Style Selection */}
          <div className="space-y-2">
            <label className="text-white text-lg">Select Style</label>
            <select
              name="roomStyle"
              value={formData.roomStyle}
              onChange={(e) => handleChange(e.target.value.toLowerCase(), "roomStyle")}
              className="w-full p-3 rounded-md bg-white text-[#007B82] cursor-pointer"
              required
            >
              <option value="">Select a style</option>
              {styles[activeTab].map((style) => (
                <option key={style} value={style.toLowerCase()}>
                  {style.charAt(0).toUpperCase() + style.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Number of designs */}
          <div className="space-y-2">
            <label className="text-white text-lg">Number of Designs</label>
            <select
              name="numDesigns"
              value={formData.numDesigns}
              onChange={(e) => handleChange(e.target.value, "numDesigns")}
              className="w-full p-3 rounded-md bg-white text-[#007B82] cursor-pointer"
            >
              {[...Array(12).keys()].map((num) => (
                <option key={num + 1} value={num + 1}>
                  {num + 1}
                </option>
              ))}
            </select>
          </div>

          {/* AI Strength */}
          <div className="space-y-2">
            <label className="text-white text-lg">AI Styling Strength</label>
            <div className="flex flex-wrap gap-3">
              {["Very Low", "Low", "Medium", "High"].map((level) => (
                <div
                  key={level}
                  className={`flex-1 min-w-[120px] px-4 py-2 rounded-md cursor-pointer text-center ${formData.aiStrength === level.toLowerCase()
                    ? "bg-white text-[#007B82]"
                    : "bg-[#00000033] text-[#FFFFFF80]"
                    }`}
                  onClick={() => handleChange(level.toLowerCase(), "aiStrength")}
                >
                  {level}
                </div>
              ))}
            </div>
          </div>
        </form>
      </div>

      {/* Generate Button */}

      <div
        className="w-full max-w-[899px] min-h-[67px] rounded-[8px] border border-[#FFFFFF4D] flex justify-center items-center cursor-pointer"
        style={{
          backgroundImage:
            "linear-gradient(to right, #007c82 0%, rgb(4, 68, 75), rgb(3, 89, 94) 100%)",
        }}

      >
        <button
          type="submit"
          onClick={handleSubmit}
          className="w-[200px] min-h-[35px] flex justify-center items-center gap-[10px] text-[20px] font-bold leading-[35px] tracking-[0.5px] text-center text-white"
        >
          <span>
            <img src={Magic} alt="magic" />
          </span>
          Generate Design
        </button>
      </div>
    </section >
  );
}
