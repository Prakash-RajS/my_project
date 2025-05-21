// import React, { useContext, useRef, useState } from "react";
// import sec7Model1 from "../../assets/home/sec7/mdi_sofa.png";
// import sec7Model2 from "../../assets/home/sec7/healthicons_home.png";
// import sec7Model3 from "../../assets/home/sec7/mdi_plant.png";
// import sec7Icon1 from "../../assets/home/sec7/solar_upload-outline.png";
// import sec7Icon2 from "../../assets/home/sec7/basil_image-solid (1).png";
// import { UserContext } from "../../context/UserContext";
// import { useNavigate } from "react-router-dom";
// import Interior from "../../assets/product-pg/Vector.png"
// import Home from "../../assets/product-pg/home.png"
// import Tree from "../../assets/product-pg/tree.png"
// import Lock from "../../assets/product-pg/lock.png"
// import Galley from "../../assets/product-pg/gallery.png"
// import I from "../../assets/product-pg/i.png"
// import Magic from "../../assets/product-pg/magic.png"

// export default function Form() {
//   const { userInfo } = useContext(UserContext);
//   const navigave = useNavigate();

//   const [formData, setFormData] = useState({
//     buildingType: "",
//     roomType: "",
//     roomStyle: "",
//     noOfDesign: "",
//     aiTouch: "",
//   });
//   const [imgURL, setImgURL] = useState(null);
//   const inpRef = useRef(null);

//   const changeImage = (e) => {
//     if (!userInfo.userId) {
//       return navigave("/sign-in");
//     }
//     const file = e.target.files[0];
//     if (file) {
//       const preview = URL.createObjectURL(file);
//       setImgURL(preview);
//     }
//   };

//   const handleDragOver = (e) => {
//     e.preventDefault();
//   };

//   const handleDrop = (e) => {
//     e.preventDefault();
//     if (!userInfo.userId) {
//       return navigave("/sign-in");
//     }
//     const file = e.dataTransfer.files[0];

//     if (file && file.type.startsWith("image/")) {
//       const preview = URL.createObjectURL(file);
//       setImgURL(preview);
//     } else {
//       alert("Please drop only image files.");
//     }
//   };

//   const handleChange = (value, key) => {
//     setFormData((prev) => {
//       return { ...prev, [key]: value };
//     });
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     if (!userInfo.userId) {
//       return navigave("/sign-in");
//     }
//     if (
//       formData.aiTouch &&
//       formData.noOfDesign &&
//       formData.roomStyle &&
//       formData.roomType &&
//       formData.buildingType &&
//       imgURL
//     ) {
//       console.log(formData);
//       console.log(imgURL);
//       setFormData({
//         buildingType: "",
//         roomType: "",
//         roomStyle: "",
//         noOfDesign: "",
//         aiTouch: "",
//       });
//       setImgURL(null);
//     } else {
//       alert("Please Fillout All The Fields!");
//     }
//   };
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

export default function Form() {
  const { userInfo } = useContext(UserContext);
  const navigate = useNavigate();
  const inpRef = useRef(null);

  const [activeTab, setActiveTab] = useState("Interiors");
  const [formData, setFormData] = useState({
    buildingType: "",
    roomType: "",
    roomStyle: "",
    noOfDesign: "1",
    aiTouch: "Low",
  });
  const [imgURL, setImgURL] = useState(null);

  const tabs = [
    { name: "Interiors", icon: Interior },
    { name: "Exteriors", icon: Home },
    { name: "Outdoors", icon: Tree },
    { name: "Upgrade to Unlock", icon: Lock },
  ];

  const roomTypes = {
    Interiors: [
      "Living room",
      "Bedroom",
      "Kitchen",
      "Dining Room",
      "Study Room",
      "Home Office",
      "Family Room",
      "Kids Room",
      "Balcony",
    ],
    Exteriors: [
      "Front Yard",
      "Backyard",
      "Garden",
      "Patio",
      "Deck",
      "Pool Area",
      "Driveway",
    ],
    Outdoors: [
      "Park",
      "Camping Site",
      "Beach",
      "Mountain View",
      "Forest",
      "Lake Side",
    ],
  };

  const styles = [
    "Modern",
    "Tropical",
    "Rustic",
    "Tribal",
    "Cyberpunk",
    "Zen",
    "Japanese Design",
    "Biophilic",
    "Christmas",
    "Bohemian",
    "Contemporary",
    "Maximalist",
    "Vintage",
    "Baroque",
    "Farmhouse",
    "Minimalist",
    "Gaming Room",
    "French Country",
    "Art Deco",
    "Art Nouveau",
    "Halloween",
    "Ski Chalet",
    "Sketch",
    "Scandinavian",
    "Industrial",
    "Neoclassic",
    "Medieval",
    "Shabby Chic",
    "Eclectic",
    "Asian Traditional",
    "Hollywood Glam",
    "Western Traditional",
    "Transitional",
  ];

  const changeImage = (e) => {
    // if (!userInfo.userId) {
    //   return navigate("/sign-in");
    // }
    const file = e.target.files[0];
    if (file) {
      const preview = URL.createObjectURL(file);
      setImgURL(preview);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    // if (!userInfo.userId) {
    //   return navigate("/sign-in");
    // }
    const file = e.dataTransfer.files[0];

    if (file && file.type.startsWith("image/")) {
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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!userInfo.userId) {
      return navigate("/sign-in");
    }
    if (
      formData.aiTouch &&
      formData.noOfDesign &&
      formData.roomStyle &&
      formData.roomType &&
      formData.buildingType &&
      imgURL
    ) {
      console.log("Form Data:", formData);
      console.log("Image URL:", imgURL);
      // Here you would typically send the data to your backend
      alert("Design generation started!");
      // Reset form
      setFormData({
        buildingType: "",
        roomType: "",
        roomStyle: "",
        noOfDesign: "1",
        aiTouch: "Low",
      });
      setImgURL(null);
    } else {
      alert("Please fill out all the fields!");
    }
  };
  


  return (
    // <section className="max-w-[100vw] w-full flex justify-center items-center bg-[#002628]">
    //   <div className="w-[1280px] p-10 pt-20 pb-20">
    //     <div
    //       className="max-w-screen-xl w-full min-h-[287px] flex flex-col justify-center items-center gap-5 rounded-t-[20px]"
    //       style={{
    //         background:
    //           "linear-gradient(to bottom, #007c82 0%, #004245 50%, #00292b 100%)",
    //       }}
    //     >
    //       <h1 className="max-w-[658px] w-full min-h-[53px] text-[38px] font-bold leading-[140%] tracking-widest tracking-[60%] text-center text-white">
    //         PICK YOUR STYLE
    //       </h1>
    //       <div className="max-w-[658px] w-full h-auto flex justify-evenly items-center">
    //         <div className="max-w-[101px] min-h-[121px] flex flex-col justify-center items-center gap-5">
    //           {" "}
    //           {/* interiors */}
    //           <div className="img">
    //             <img src={sec7Model1} alt="interiors" />
    //           </div>
    //           <p className="max-w-[101px] min-h-[31px] text-[22px] font-semibold leading-[140%] text-center text-[white]">
    //             Interiors
    //           </p>
    //         </div>
    //         <div className="max-w-[101px] min-h-[121px] flex flex-col justify-center items-center gap-5">
    //           {" "}
    //           {/* exteriors */}
    //           <div className="img">
    //             <img src={sec7Model2} alt="exteriors" />
    //           </div>
    //           <p className="max-w-[101px] min-h-[31px] text-[22px] font-semibold leading-[140%] text-center text-[white]">
    //             Exteriors
    //           </p>
    //         </div>
    //         <div className="max-w-[101px] min-h-[121px] flex flex-col justify-center items-center gap-5">
    //           <div className="img">
    //             <img src={sec7Model3} alt="outdoors" />
    //           </div>
    //           <p className="max-w-[101px] min-h-[31px] text-[22px] font-semibold leading-[140%] text-center text-[white]">
    //             Outdoors
    //           </p>
    //         </div>
    //       </div>
    //     </div>

    //     <div className="max-w-screen-xl min-h-[912px]  shadow-[0px_0px_4px_opx_#00000059] flex justify-center rounded-none items-center ">
    //       <div className=" bg-[#002628] w-full min-h-[868px] flex justify-center items-center gap-5 max-[1100px]:flex-col p-5 max-[400px]:p-3 rounded-br-[20px] rounded-bl-[20px]">
    //         <div className="flex-1 w-full min-h-[400px] p-4 min-[500px]:min-h-[868px] bg-[#00393D] flex justify-center items-center rounded-[10px]">
    //           <input
    //             type="file"
    //             ref={inpRef}
    //             accept="image/*"
    //             hidden
    //             onChange={changeImage}
    //           />

    //           <div className="flex-1 w-full min-[500px]:min-h-[795px] flex flex-col justify-center items-center gap-[30px]">
    //             <div className="max-w-[550px] w-full min-w-[55px] flex justify-center items-start ">
    //               <div
    //                 className="max-w-[235px] w-full min-h-[40px] flex justify-center items-center px-5 py-2 rounded-[20px] gap-1"
    //                 style={{
    //                   background:
    //                     "linear-gradient(to right, rgb(0, 176, 186) 0%, rgba(0, 0, 0, 0) 50%, rgb(0, 176, 186) 100%)",
    //                 }}
    //               >
    //                 <img
    //                   src={sec7Icon1}
    //                   alt=""
    //                   className="max-w-[21.5px] min-h-[21.5px]"
    //                 />
    //                 <button
    //                   // onClick={() => {
    //                   //   if (!userInfo.userId) {
    //                   //     return navigave("/sign-in");
    //                   //   }
    //                   //   inpRef.current.click();
    //                   // }}
    //                   className="max-w-[235px] min-h-[40px] text-[16px] font-semibold leading-[140%] text-center text-white"
    //                 >
    //                   Step 1 : Upload images
    //                 </button>
    //               </div>
    //             </div>

    //             <div
    //               className={`max-w-[550px] w-full min-h-[300px] min-[500px]:min-h-[740px] p-2 md:p-10 border ${
    //                 imgURL ? "cursor-default" : "cursor-pointer"
    //               } flex flex-col justify-center items-center rounded-sm border-[white] border-dashed`}
    //               onClick={() => {
    //                 if (!userInfo.userId) {
    //                   return navigave("/sign-in");
    //                 }
    //                 !imgURL && inpRef.current.click();
    //               }}
    //               onDragOver={handleDragOver}
    //               onDrop={handleDrop}
    //             >
    //               {imgURL ? (
    //                 <div className="w-full p-3 sm:p-5">
    //                   <div className="flex items-stretch justify-evenly mb-10 md:mb-20">
    //                     <div className="flex flex-col items-center cursor-pointer justify-start gap-1 flex-1">
    //                       <div
    //                         className="p-3 rounded-full bg-[#007B824D]"
    //                         onClick={() => {
    //                           if (!userInfo.userId) {
    //                             return navigave("/sign-in");
    //                           }
    //                           inpRef.current.click();
    //                         }}
    //                       >
    //                         <svg
    //                           xmlns="http://www.w3.org/2000/svg"
    //                           width="19"
    //                           height="19"
    //                           viewBox="0 0 19 16"
    //                           fill="none"
    //                         >
    //                           <path
    //                             fillRule="evenodd"
    //                             clipRule="evenodd"
    //                             d="M4.68257 0.205106C7.83164 -0.0683688 10.9985 -0.0683688 14.1476 0.205106L15.6576 0.337106C16.3595 0.398572 17.0203 0.694319 17.5338 1.17678C18.0473 1.65925 18.3835 2.30039 18.4886 2.99711C18.9421 6.01348 18.9421 9.08073 18.4886 12.0971C18.4479 12.3618 18.3772 12.6131 18.2766 12.8511C18.2106 13.0081 18.0066 13.0321 17.8906 12.9061L13.4696 8.04211C13.3718 7.93458 13.2449 7.85777 13.1043 7.82102C12.9637 7.78427 12.8154 7.78917 12.6776 7.83511L10.1466 8.67911L6.47557 4.54911C6.40766 4.47271 6.32486 4.41099 6.23224 4.36776C6.13962 4.32452 6.03914 4.30067 5.93697 4.29767C5.8348 4.29467 5.7331 4.31259 5.6381 4.35033C5.54311 4.38806 5.45683 4.44482 5.38457 4.51711L0.470566 9.43111C0.437183 9.46542 0.394513 9.48925 0.347787 9.49967C0.301061 9.51009 0.252311 9.50664 0.207512 9.48977C0.162713 9.47289 0.123812 9.4433 0.0955791 9.40464C0.0673461 9.36598 0.0510076 9.31992 0.0485665 9.27211C-0.0696914 7.17563 0.0281576 5.07255 0.340567 2.99611C0.445587 2.29939 0.78188 1.65825 1.29536 1.17578C1.80884 0.693319 2.46967 0.397572 3.17157 0.336106L4.68257 0.205106ZM11.4146 4.54711C11.4146 4.14928 11.5726 3.76775 11.8539 3.48645C12.1352 3.20514 12.5167 3.04711 12.9146 3.04711C13.3124 3.04711 13.6939 3.20514 13.9752 3.48645C14.2565 3.76775 14.4146 4.14928 14.4146 4.54711C14.4146 4.94493 14.2565 5.32646 13.9752 5.60777C13.6939 5.88907 13.3124 6.04711 12.9146 6.04711C12.5167 6.04711 12.1352 5.88907 11.8539 5.60777C11.5726 5.32646 11.4146 4.94493 11.4146 4.54711Z"
    //                             fill="white"
    //                           />
    //                           <path
    //                             d="M0.375073 11.6471C0.348065 11.6744 0.327703 11.7076 0.315564 11.744C0.303424 11.7804 0.299835 11.8191 0.305073 11.8571L0.340073 12.0971C0.445094 12.7938 0.781386 13.435 1.29487 13.9175C1.80835 14.3999 2.46918 14.6957 3.17107 14.7571L4.68107 14.8881C7.83107 15.1621 10.9971 15.1621 14.1471 14.8881L15.6571 14.7571C16.0713 14.7221 16.4743 14.6041 16.8421 14.4101C16.9791 14.3391 17.0021 14.1581 16.8981 14.0441L12.7981 9.53414C12.7655 9.49793 12.7231 9.47202 12.676 9.45958C12.6289 9.44715 12.5793 9.44873 12.5331 9.46414L10.1511 10.2581C10.0118 10.3046 9.86197 10.3092 9.72011 10.2714C9.57826 10.2335 9.45064 10.1549 9.35307 10.0451L6.05807 6.33814C6.03539 6.31266 6.00773 6.2921 5.9768 6.27772C5.94588 6.26333 5.91233 6.25543 5.87823 6.25449C5.84414 6.25355 5.81021 6.2596 5.77854 6.27227C5.74687 6.28494 5.71812 6.30395 5.69407 6.32814L0.375073 11.6471Z"
    //                             fill="white"
    //                           />
    //                         </svg>
    //                       </div>
    //                       <p className="text-[12px] text-white font-medium text-center">
    //                         Change Image
    //                       </p>
    //                     </div>
    //                     <div className="flex flex-col items-center cursor-pointer justify-start gap-1 flex-1">
    //                       <div className="p-3 rounded-full bg-[#007B824D]">
    //                         <svg
    //                           xmlns="http://www.w3.org/2000/svg"
    //                           width="21"
    //                           height="21"
    //                           viewBox="0 0 21 21"
    //                           fill="none"
    //                         >
    //                           <path
    //                             d="M20 20L15.514 15.506M18 9.5C18 11.7543 17.1045 13.9163 15.5104 15.5104C13.9163 17.1045 11.7543 18 9.5 18C7.24566 18 5.08365 17.1045 3.48959 15.5104C1.89553 13.9163 1 11.7543 1 9.5C1 7.24566 1.89553 5.08365 3.48959 3.48959C5.08365 1.89553 7.24566 1 9.5 1C11.7543 1 13.9163 1.89553 15.5104 3.48959C17.1045 5.08365 18 7.24566 18 9.5Z"
    //                             stroke="white"
    //                             strokeWidth="2"
    //                             strokeLinecap="round"
    //                           />
    //                         </svg>
    //                       </div>
    //                       <p className="text-[12px] text-white font-medium text-center">
    //                         Show
    //                       </p>
    //                     </div>
    //                     <div className="flex flex-col items-center cursor-pointer justify-start gap-1 flex-1">
    //                       <div
    //                         className="p-3 rounded-full bg-[#007B824D]"
    //                         onClick={() => {
    //                           setImgURL(null);
    //                         }}
    //                       >
    //                         <svg
    //                           xmlns="http://www.w3.org/2000/svg"
    //                           width="17"
    //                           height="20"
    //                           viewBox="0 0 17 20"
    //                           fill="none"
    //                         >
    //                           <path
    //                             d="M11.491 1.471L11.784 3.5H15.75C15.9489 3.5 16.1397 3.57902 16.2803 3.71967C16.421 3.86032 16.5 4.05109 16.5 4.25C16.5 4.44891 16.421 4.63968 16.2803 4.78033C16.1397 4.92098 15.9489 5 15.75 5H14.981L14.108 15.185C14.055 15.805 14.012 16.315 13.943 16.727C13.873 17.156 13.766 17.54 13.557 17.896C13.2288 18.4551 12.7409 18.9033 12.156 19.183C11.784 19.36 11.392 19.433 10.958 19.467C10.541 19.5 10.03 19.5 9.408 19.5H7.092C6.47 19.5 5.959 19.5 5.542 19.467C5.108 19.433 4.716 19.36 4.344 19.183C3.75908 18.9033 3.27118 18.4551 2.943 17.896C2.733 17.54 2.628 17.156 2.557 16.727C2.488 16.314 2.445 15.805 2.392 15.185L1.519 5H0.75C0.551088 5 0.360322 4.92098 0.21967 4.78033C0.0790175 4.63968 0 4.44891 0 4.25C0 4.05109 0.0790175 3.86032 0.21967 3.71967C0.360322 3.57902 0.551088 3.5 0.75 3.5H4.716L5.009 1.471L5.02 1.41C5.202 0.62 5.88 0 6.73 0H9.77C10.62 0 11.298 0.62 11.48 1.41L11.491 1.471ZM6.231 3.5H10.268L10.012 1.724C9.964 1.557 9.842 1.5 9.769 1.5H6.731C6.658 1.5 6.536 1.557 6.488 1.724L6.231 3.5ZM7.5 8.25C7.5 8.05109 7.42098 7.86032 7.28033 7.71967C7.13968 7.57902 6.94891 7.5 6.75 7.5C6.55109 7.5 6.36032 7.57902 6.21967 7.71967C6.07902 7.86032 6 8.05109 6 8.25V13.25C6 13.4489 6.07902 13.6397 6.21967 13.7803C6.36032 13.921 6.55109 14 6.75 14C6.94891 14 7.13968 13.921 7.28033 13.7803C7.42098 13.6397 7.5 13.4489 7.5 13.25V8.25ZM10.5 8.25C10.5 8.05109 10.421 7.86032 10.2803 7.71967C10.1397 7.57902 9.94891 7.5 9.75 7.5C9.55109 7.5 9.36032 7.57902 9.21967 7.71967C9.07902 7.86032 9 8.05109 9 8.25V13.25C9 13.4489 9.07902 13.6397 9.21967 13.7803C9.36032 13.921 9.55109 14 9.75 14C9.94891 14 10.1397 13.921 10.2803 13.7803C10.421 13.6397 10.5 13.4489 10.5 13.25V8.25Z"
    //                             fill="white"
    //                           />
    //                         </svg>
    //                       </div>
    //                       <p className="text-[12px] text-white font-medium text-center">
    //                         Delete
    //                       </p>
    //                     </div>
    //                   </div>

    //                   <img
    //                     src={imgURL}
    //                     className="w-full h-auto rounded-lg"
    //                     alt=""
    //                   />
    //                 </div>
    //               ) : (
    //                 <>
    //                   <img
    //                     src={sec7Icon2}
    //                     alt=""
    //                     className="max-w-[60px] min-w-[60px]"
    //                   />
    //                   <p className="max-w-[280px] min-h-[40px] text-sm leading-[140%] text-center text-white">
    //                     Drop an image,Tap to Select,Take a Photo or Paste
    //                   </p>
    //                 </>
    //               )}
    //             </div>
    //           </div>
    //         </div>

    //         <form
    //           onSubmit={handleSubmit}
    //           className="max-w-[610px] w-full min-h-[868px] flex flex-col justify-center items-center gap-[20PX]"
    //         >
    //           <div className="max-w-[610px] min-h-[516px] w-full bg-[#00393D] flex flex-col justify-center items-center rounded-[10px] p-5">
    //             <div className="max-w-[610px] w-full min-h-[75px]  flex justify-center items-center">
    //               <div
    //                 className="max-w-[292px] min-h-[40px] flex justify-center items-center px-6 py-4 rounded-[40px] gap-2"
    //                 style={{
    //                   background:
    //                     "linear-gradient(to right,#00b0ba 0%,#0000001a 50%,#007b82 100%)",
    //                 }}
    //               >
    //                 <img src={sec7Model2} alt="" className="w-6 h-6" />
    //                 <p className="max-w-[220px] min-h-[22px] text-[16px] font-semibold leading-[140%] text-center text-white">
    //                   Step2 : Design or Customize
    //                 </p>
    //               </div>
    //             </div>

    //             <div className="max-w-[550px] w-full min-h-[389px] flex flex-col justify-center items-center gap-[31px]">
    //               <div className="max-w-[550px] w-full flex flex-col justify-center items-center gap-2.5">
    //                 <p className="max-w-[550px] w-full min-h-[22px] text-base font-normal leading-[140%] text-white">
    //                   Select Building Type
    //                 </p>
    //                 <div className="max-w-[550px] w-full min-h-[42px] flex justify-between items-center gap-3">
    //                   <label
    //                     htmlFor="btype1"
    //                     className="max-w-[255px] w-full min-h-[42px] rounded bg-[#00000033] flex justify-between items-center px-2.5 py-0 hover:bg-white group"
    //                   >
    //                     <span className="group-hover:text-[#007b82] text-[white] max-w-[92px] min-h-[22px] text-base font-medium leading-[140%] text-center">
    //                       Commercial
    //                     </span>{" "}
    //                     <input
    //                       type="radio"
    //                       name="buildingType"
    //                       id="btype1"
    //                       value="commercial"
    //                       checked={formData.buildingType === "commercial"}
    //                       onChange={(e) => {
    //                         handleChange(e.target.value, "buildingType");
    //                       }}
    //                     />
    //                   </label>
    //                   <label
    //                     htmlFor="btype2"
    //                     className="max-w-[255px] w-full min-h-[42px] rounded bg-[#00000033] flex justify-between items-center px-2.5 py-0 hover:bg-white group"
    //                   >
    //                     <span className="group-hover:text-[#007b82] text-[white] max-w-[92px] min-h-[22px] text-base font-medium leading-[140%] text-center">
    //                       Residential
    //                     </span>{" "}
    //                     <input
    //                       type="radio"
    //                       name="buildingType"
    //                       id="btype2"
    //                       value="residential"
    //                       checked={formData.buildingType === "residential"}
    //                       onChange={(e) => {
    //                         handleChange(e.target.value, "buildingType");
    //                       }}
    //                     />
    //                   </label>
    //                 </div>
    //               </div>

    //               <div className="max-w-[550px] w-full flex flex-col justify-center items-center gap-2.5">
    //                 <p className="max-w-[550px] w-full min-h-[22px] text-base leading-[140%] font-normal text-white text-start">
    //                   Room Type
    //                 </p>
    //                 <div className="max-w-[550px] w-full min-h-[42px] h-full rounded flex justify-between items-center bg-white text-black px-4 py-2.5">
    //                   <select
    //                     required
    //                     value={formData.roomType}
    //                     onChange={(e) => {
    //                       handleChange(e.target.value, "roomType");
    //                     }}
    //                     className="w-full bg-white"
    //                   >
    //                     <option value=""></option>
    //                     <option value="Bedroom">Bedroom</option>
    //                     <option value="Kitchen">Kitchen</option>
    //                     <option value="Dining Room">Dining Room</option>
    //                     <option value="Study Room">Study Room</option>
    //                     <option value="Home Office">HOME Office</option>
    //                     <option value="Family Room">Family Room</option>
    //                     <option value="Kids Room">Kids Room</option>
    //                     <option value="Balcony">Balcony</option>
    //                   </select>
    //                 </div>
    //               </div>

    //               <div className="max-w-[550px] w-full flex flex-col justify-center items-center gap-2.5">
    //                 <p className="max-w-[550px] w-full min-h-[22px] text-base leading-[140%] font-normal text-white text-start">
    //                   Room Style
    //                 </p>
    //                 <div className="max-w-[550px] w-full min-h-[42px] h-full rounded flex justify-between items-center bg-white text-black px-4 py-2.5">
    //                   <select
    //                     required
    //                     value={formData.roomStyle}
    //                     onChange={(e) => {
    //                       handleChange(e.target.value, "roomStyle");
    //                     }}
    //                     className="w-full bg-white"
    //                   >
    //                     <option value=""></option>
    //                     <option value="Midcentury Modern">
    //                       Midcentury Modern
    //                     </option>
    //                     <option value="Modern">Modern</option>
    //                     <option value="Tropical">Tropical</option>
    //                     <option value="Rustic">Rustic</option>
    //                     <option value="Tribal">Tribal</option>
    //                     <option value="Cyberpunk">Cyberpunk</option>
    //                     <option value="Zen">Zen</option>
    //                     <option value="Japanese Design">Japanese Design</option>
    //                     <option value="Biophilic">Biophilic</option>
    //                     <option value="Christimas">Christimas</option>
    //                     <option value="Bohemian">Bohemian</option>
    //                     <option value="Contemporary">Contemporary</option>
    //                     <option value="Maximalist">Maximalist</option>
    //                     <option value="Vintage">Vintage</option>
    //                     <option value="Baroque">Baroque</option>
    //                     <option value="Farmhouse">Farmhouse</option>
    //                     <option value="Minimalist">Minimalist</option>
    //                     <option value="Gaming Room">Gaming Room</option>
    //                     <option value="French Country">French Country</option>
    //                     <option value="Art Deco">Art Deco</option>
    //                     <option value="Art Nouveau">Art Nouveau</option>
    //                     <option value="Halloween">Halloween</option>
    //                     <option value="Ski Chalet">Ski Chalet</option>
    //                     <option value="Sketch">Sketch</option>
    //                     <option value="Scandinavian">Scandinavian</option>
    //                     <option value="Industrial">Industrial</option>
    //                     <option value="Neoclassic">Neoclassic</option>
    //                     <option value="Medieval">Medieval</option>
    //                     <option value="Shabby Chic">Shabby Chic</option>
    //                     <option value="Eclectic">Eclectic</option>
    //                     <option value="Asian Traditional">
    //                       Asian Traditional
    //                     </option>
    //                     <option value="Hollywood Glam">Hollywood Glam</option>
    //                     <option value="Western Traditional">
    //                       Western Traditional
    //                     </option>
    //                     <option value="Transitional">Transitional</option>
    //                   </select>
    //                 </div>
    //               </div>

    //               <div className="max-w-[550px] w-full flex flex-col justify-center items-center gap-2.5">
    //                 <p className="max-w-[550px] w-full min-h-[22px] text-base leading-[140%] font-normal text-white text-start">
    //                   Number Of Design
    //                 </p>
    //                 <div className="max-w-[550px] w-full min-h-[42px] h-full rounded flex justify-between items-center bg-white text-black px-4 py-2.5">
    //                   <input
    //                     type="number"
    //                     value={formData.noOfDesign}
    //                     onChange={(e) => {
    //                       handleChange(e.target.value, "noOfDesign");
    //                     }}
    //                     className="w-full"
    //                   />
    //                 </div>
    //               </div>
    //             </div>
    //           </div>

    //           <div className="max-w-[610px] min-h-[332px] w-full bg-[#00393D] flex flex-col justify-center items-center rounded-[10px] p-5">
    //             <div className="max-w-[610px] w-full min-h-[75px] flex justify-center items-center">
    //               <div
    //                 className="max-w-[292px] min-h-[40px] flex justify-center items-center px-5 py-4 rounded-[40px] gap-2"
    //                 style={{
    //                   background:
    //                     "linear-gradient(to right,#00b0ba 0%,#0000001a 50%,#007b82 100%)",
    //                 }}
    //               >
    //                 <img src={step3} alt="" className="w-6 h-6" />
    //                 <p className="max-w-[220px] min-h-[22px] text-[16px] font-semibold leading-[140%] text-center text-white">
    //                   Step3 : Generate new Design
    //                 </p>
    //               </div>
    //             </div>

    //             <div className="max-w-[550px] w-full min-h-[240px] flex flex-col justify-center items-center gap-[31px]">
    //               <div className="max-w-[550px] w-full flex flex-col justify-center items-center gap-5">
    //                 <p className="max-w-[550px] w-full min-h-[22px] text-base font-normal leading-[140%] text-white">
    //                   AI Touch
    //                 </p>
    //                 <div className="max-w-[550px] w-full min-h-[42px] flex justify-between items-center gap-3">
    //                   <label
    //                     htmlFor="btype3"
    //                     className="max-w-[255px] w-full min-h-[42px] rounded bg-[#00000033] flex justify-between items-center px-2.5 py-0 hover:bg-white group cursor-pointer"
    //                   >
    //                     <span className="text-[white] max-w-[92px] min-h-[22px] text-base font-medium leading-[140%] text-center group-hover:text-[#007b82]">
    //                       Very Low
    //                     </span>{" "}
    //                     <input
    //                       type="radio"
    //                       value="veryLow"
    //                       onChange={(e) => {
    //                         handleChange(e.target.value, "aiTouch");
    //                       }}
    //                       checked={formData.aiTouch === "veryLow"}
    //                       name="aiTouch"
    //                       id="btype3"
    //                     />
    //                   </label>
    //                   <label
    //                     htmlFor="btype4"
    //                     className="max-w-[255px] w-full min-h-[42px] rounded bg-[#00000033] flex justify-between items-center px-2.5 py-0 hover:bg-white group cursor-pointer"
    //                   >
    //                     <span className="text-[white] max-w-[92px] min-h-[22px] text-base font-medium leading-[140%] text-center group-hover:text-[#007b82]">
    //                       Low
    //                     </span>{" "}
    //                     <input
    //                       type="radio"
    //                       value="low"
    //                       onChange={(e) => {
    //                         handleChange(e.target.value, "aiTouch");
    //                       }}
    //                       checked={formData.aiTouch === "low"}
    //                       name="aiTouch"
    //                       id="btype4"
    //                     />
    //                   </label>
    //                 </div>
    //                 <div className="max-w-[550px] w-full min-h-[42px] flex justify-between items-center gap-3">
    //                   <label
    //                     htmlFor="btype5"
    //                     className="max-w-[255px] w-full min-h-[42px] rounded bg-[#00000033] flex justify-between items-center px-2.5 py-0 hover:bg-white group cursor-pointer"
    //                   >
    //                     <span className="text-[white] max-w-[92px] min-h-[22px] text-base font-medium leading-[140%] text-center group-hover:text-[#007b82]">
    //                       Medium
    //                     </span>{" "}
    //                     <input
    //                       type="radio"
    //                       value="medium"
    //                       onChange={(e) => {
    //                         handleChange(e.target.value, "aiTouch");
    //                       }}
    //                       checked={formData.aiTouch === "medium"}
    //                       name="aiTouch"
    //                       id="btype5"
    //                     />
    //                   </label>
    //                   <label
    //                     htmlFor="btype6"
    //                     className="max-w-[255px] w-full min-h-[42px] rounded bg-[#00000033] flex justify-between items-center px-2.5 py-0 hover:bg-white group cursor-pointer"
    //                   >
    //                     <span className="text-[white] max-w-[92px] min-h-[22px] text-base font-medium leading-[140%] text-center group-hover:text-[#007b82]">
    //                       High
    //                     </span>{" "}
    //                     <input
    //                       type="radio"
    //                       value="high"
    //                       onChange={(e) => {
    //                         handleChange(e.target.value, "aiTouch");
    //                       }}
    //                       checked={formData.aiTouch === "high"}
    //                       name="aiTouch"
    //                       id="btype6"
    //                     />
    //                   </label>
    //                 </div>
    //               </div>
    //               <div
    //                 className="max-w-[570px] w-full min-h-[54px] border-2 border-[#FFFFFF4D] bg-[#00B0BAC] flex justify-center items-center gap-2.5 cursor-pointer rounded-[5px] border-solid border-[white_30%]"
    //                 style={{
    //                   background:
    //                     "linear-gradient(to right,#00b0ba 0%,#0000004d 50%,#007b82 100%)",
    //                 }}
    //               >
    //                 <img src={sec7Icon3} alt="" />
    //                 <button type="submit" className="text-white cursor-pointer">
    //                   Create Magic
    //                 </button>
    //               </div>
    //             </div>
    //           </div>
    //         </form>
    //       </div>
    //     </div>
    //   </div>
    // </section>


   //  <section className="w-[full] max-w-[full] min-h-[1216px] px-[86px] py-[68px] flex flex-col justify-start items-center gap-[40px] bg-gradient-to-l from-[#002628] to-[#00646A]">
   //    <div className="max-w-[1268px] min-h-[113px]">
   //        <div className="max-w-[1268px] min-h-[67px] font-semibold text-[48px] leading-[140%] text-center text-white">Let AI Style It</div>
   //        <div className="max-w-[1268px] min-h-[34px] font-semibold text-[24px] leading-[140%] text-center text-white">Upload a photo to begin your AI-powered room design</div>
   //    </div>

   //    <div className="max-w-[1268px] min-h-[150px] flex flex-col items-center justify-start">
   //        <div className="max-w-[920px] min-h-[128px] flex justify-center items-center gap-[40px] flex-wrap">
   //           <div className="w-[200px] h-[128px] flex flex-col justify-center items-center gap-[20px]">
   //              <div className="w-[80px] h-[77px] border-[2px] border-solid border-white px-[20px] py-[24px] flex justify-center items-center gap-[10px] bg-gradient-to-l from-[#00B0BA] via-[#000000] to-[#007B82] rounded-[90px] transition-all duration-200
   //                              ${activeIndex === index ? 'border-[2px] border-solid border-white' : 'border border-transparent'}
   //                               hover:border-blue-300`">
   //                 <img src={Interior} alt="sofa" />
   //              </div>
   //              <div className="max-w-[200px] min-h-[31px] text-[22px] font-semibold leading-[140%] text-center text-white">
   //                 Interiors
   //              </div>

   //           </div>
   //           <div className="w-[200px] h-[128px] flex flex-col justify-center items-center gap-[20px]">
   //              <div className="w-[80px] h-[77px] border-[2px]  border-white px-[20px] py-[24px] flex justify-center items-center gap-[10px] bg-[#FFFFFF1A] rounded-[90px] transition-all duration-200
   //                              ${activeIndex === index ? 'border-[2px]  border-white' : 'border border-transparent'}
   //                               hover:border-blue-300`">
   //                 <img src={Home} alt="sofa" />
   //              </div>
   //              <div className="max-w-[200px] min-h-[31px] text-[22px] font-semibold leading-[140%] text-center text-white">
   //                 Exteriors
   //              </div>

   //           </div>
   //           <div className="w-[200px] h-[128px] flex flex-col justify-center items-center gap-[20px]">
   //              <div className="w-[80px] h-[77px] border-[2px]  border-white px-[20px] py-[24px] flex justify-center items-center gap-[10px] bg-[#FFFFFF1A] rounded-[90px] transition-all duration-200
   //                              ${activeIndex === index ? 'border-[2px] border-white' : 'border border-transparent'}
   //                               hover:border-blue-300`">
   //                 <img src={Tree} alt="sofa" />
   //              </div>
   //              <div className="max-w-[200px] min-h-[31px] text-[22px] font-semibold leading-[140%] text-center text-white">
   //                 Outdoors
   //              </div>

   //           </div>
   //           <div className="w-[200px] h-[128px] flex flex-col justify-center items-center gap-[20px]">
   //              <div className="w-[80px] h-[77px] border-[2px]  border-white px-[20px] py-[24px] flex justify-center items-center gap-[10px] bg-[#FFFFFF1A] rounded-[90px] transition-all duration-200
   //                              ${activeIndex === index ? 'border-[2px]  border-white' : 'border border-transparent'}
   //                               hover:border-blue-300`">
   //                 <img src={Lock} alt="sofa" />
   //              </div>
   //              <div className="max-w-[200px] min-h-[31px] text-[22px] font-semibold leading-[140%] text-center text-white">
   //                 Upgrade to Unlock
   //              </div>
   //           </div>
   //        </div>

   //    </div>

   //    <div className="max-w-[1268px] min-h-[727px] flex flex-col justify-start items-center gap-[56px]">
   //       <div className="max-w-[1268px] min-h-[604px] flex justify-between items-center gap-[82px] flex-wrap">
   //         <div className="max-w-[636px] min-h-[604px] flex flex-col justify-center items-center gap-[12px]">
   //            <div className="w-[636px] min-h-[552px] rounded-[12px] border-[1px] border-dashed border-white flex justify-center items-center">
   //               <div className="w-[280px] min-h-[133px] flex flex-col justify-center items-center">
   //                  <div className="w-[70px] h-[70px] rounded-[40px] px-[18px] py-[16px] rouned-[40px] bg-[#FFFFFF1A] flex justify-center items-center">
   //                    <img src={Galley} alt="gallery" />
   //                  </div>
   //                  <div className="w-[280px] h-[68px] font-[400] text-[24px] leading-[140%] text-center text-[#FFFFFFB2]">
   //                  Drag & drop or click to upload a photo
   //                  </div>
   //               </div>
   //            </div>

   //            <div className="w-[147px] h-[40px] rounded-[6px] border-[1.5px] border-solid border-white px-[10px] py-[8px] flex justify-around items-center">
   //              <div className="w-[24px] h-[24px]">
   //                 <img src={I} alt="i" />
   //              </div>
   //              <div className="w-[93px] h-[19px] text-[16px] font-[medium] leading-[100%] text-center text-white">Photo guide</div>
   //            </div>
   //         </div>

   //         <div className="w-[550px] h-[604px] flex flex-col items-start justify-start gap-[52px]">
   //           <div className="w-[550px] min-h-[411px] flex flex-col items-center justify-start gap-[31px]">
   //              <div className="w-[550px] min-h-[81px] flex flex-col justify-start items-center gap-[12px]">
   //                <div className="w-[550px] min-h-[27px] font-[400] text-[19px] leading-[140%] text-white">Choose Building Type</div>
   //                <div className="w-[100%] max-w-[550px] min-h-[42px] flex justify-between items-center">
   //                    <div className="w-full max-w-[255px] min-h-[42px] rounded-[4px] bg-[#00000033] flex justify-between items-center px-[20px]">
   //                       <span className=" w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center text-[#FFFFFF80]">Commercial</span>
   //                       <input type="radio"/>
   //                    </div>
                   
   //                    <div className="w-full max-w-[255px] min-h-[42px] rounded-[4px] bg-white flex justify-between items-center px-[20px]">
   //                       <span className=" w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center text-[#007B82]">Commercial</span>
   //                       <input type="radio"/>
   //                    </div>

   //                </div>
   //              </div>
   //              <div className="w-[550px] min-h-[81px] flex flex-col justify-start items-start gap-[12px]">
   //                <div className="w-[550px] min-h-[27px] font-[400] text-[19px] leading-[140%] text-white">	Select Room Type</div>
   //                    <div className="w-full max-w-[550px] min-h-[42px] rounded-[4px] bg-white flex justify-between items-center px-[20px] ">
   //                       <span className=" w- min-h-[22px] font-medium text-[16px] leading-[140%] text-center text-[#007B82] ">
   //                          <select name="" id="" className="w-[510px] h-[42px] cursor-pointer">
   //                           <option value="">Living room</option>
   //                           <option value="Bedroom">Bedroom</option>
   //                           <option value="Kitchen">Kitchen</option>
   //                           <option value="Dining Room">Dining Room</option>
   //                           <option value="Study Room">Study Room</option>
   //                           <option value="Home Office">HOME Office</option>
   //                           <option value="Family Room">Family Room</option>
   //                           <option value="Kids Room">Kids Room</option>
   //                           <option value="Balcony">Balcony</option>
   //                          </select>
   //                       </span>
                        
   //                    </div>                  
   //              </div>
   //              <div className="w-[550px] min-h-[81px] flex flex-col justify-start items-start gap-[12px]">
   //                <div className="w-[550px] min-h-[27px] font-[400] text-[19px] leading-[140%] text-white">	Pick a Style</div>
   //                    <div className="w-full max-w-[550px] min-h-[42px] rounded-[4px] bg-white flex justify-between items-center px-[20px] ">
   //                       <span className=" w- min-h-[22px] font-medium text-[16px] leading-[140%] text-center text-[#007B82] ">
   //                          <select name="" id="" className="w-[510px] h-[42px] cursor-pointer">
                           
   //  //                     <option value="Modern">Modern</option>
   //  //                     <option value="Tropical">Tropical</option>
   //  //                     <option value="Rustic">Rustic</option>
   //  //                     <option value="Tribal">Tribal</option>
   //  //                     <option value="Cyberpunk">Cyberpunk</option>
   //  //                     <option value="Zen">Zen</option>
   //  //                     <option value="Japanese Design">Japanese Design</option>
   //  //                     <option value="Biophilic">Biophilic</option>
   //  //                     <option value="Christimas">Christimas</option>
   //  //                     <option value="Bohemian">Bohemian</option>
   //  //                     <option value="Contemporary">Contemporary</option>
   //  //                     <option value="Maximalist">Maximalist</option>
   //  //                     <option value="Vintage">Vintage</option>
   //  //                     <option value="Baroque">Baroque</option>
   //  //                     <option value="Farmhouse">Farmhouse</option>
   //  //                     <option value="Minimalist">Minimalist</option>
   //  //                     <option value="Gaming Room">Gaming Room</option>
   //  //                     <option value="French Country">French Country</option>
   //  //                     <option value="Art Deco">Art Deco</option>
   //  //                     <option value="Art Nouveau">Art Nouveau</option>
   //  //                     <option value="Halloween">Halloween</option>
   //  //                     <option value="Ski Chalet">Ski Chalet</option>
   //  //                     <option value="Sketch">Sketch</option>
   //  //                     <option value="Scandinavian">Scandinavian</option>
   //  //                     <option value="Industrial">Industrial</option>
   //  //                     <option value="Neoclassic">Neoclassic</option>
   //  //                     <option value="Medieval">Medieval</option>
   //  //                     <option value="Shabby Chic">Shabby Chic</option>
   //  //                     <option value="Eclectic">Eclectic</option>
   //  //                     <option value="Asian Traditional">
   //  //                       Asian Traditional
   //  //                     </option>
   //  //                     <option value="Hollywood Glam">Hollywood Glam</option>
   //  //                     <option value="Western Traditional">
   //  //                       Western Traditional
   //  //                     </option>
   //  //                     <option value="Transitional">Transitional</option>
   //  //                  
   //                          </select>
   //                       </span>
                        
   //                    </div>                  
   //              </div>

   //              <div className="w-[550px] min-h-[81px] flex flex-col justify-start items-start gap-[12px]">
   //                <div className="w-[550px] min-h-[27px] font-[400] text-[19px] leading-[140%] text-white">	Number of designs</div>
   //                    <div className="w-full max-w-[550px] min-h-[42px] rounded-[4px] bg-white flex justify-between items-center px-[20px] ">
   //                       <span className=" w- min-h-[22px] font-medium text-[16px] leading-[140%] text-center text-[#007B82] ">
   //                          <select name="" id="" className="w-[510px] h-[42px] cursor-pointer">
   //                             <option value="">1</option>
   //                             <option value="">2</option>
   //                             <option value="">3</option>
   //                             <option value="">4</option>
   //                             <option value="">5</option>
   //                             <option value="">6</option>
   //                             <option value="">7</option>
   //                             <option value="">8</option>
   //                             <option value="">9</option>
   //                          </select>
   //                       </span>
   //                    </div>                  
   //              </div>
   //           </div>

   //         <div className="w-full max-w-[550px] min-h-[141px] flex flex-col justify-start items-start gap-[12px]">
   //         <div className="w-[550px] min-h-[81px] flex flex-col justify-start items-start gap-[12px]">
   //                <div className="w-[550px] min-h-[27px] font-[400] text-[19px] leading-[140%] text-white">AI Styling Strength</div>
   //                <div className="w-[100%] max-w-[550px] min-h-[42px] flex justify-between items-center">
   //                    <div className="w-full max-w-[255px] min-h-[42px] rounded-[4px] bg-[#00000033] flex justify-between items-center px-[20px]">
   //                       <span className=" w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center text-[#FFFFFF80]">Commercial</span>
   //                       <input type="radio"/>
   //                    </div>
                   
   //                    <div className="w-full max-w-[255px] min-h-[42px] rounded-[4px] bg-[#00000033] flex justify-between items-center px-[20px]">
   //                       <span className=" w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center text-[#007B82]">Commercial</span>
   //                       <input type="radio"/>
   //                    </div>

   //                </div>
   //                <div className="w-[100%] max-w-[550px] min-h-[42px] flex justify-between items-center">
   //                    <div className="w-full max-w-[255px] min-h-[42px] rounded-[4px] bg-[#00000033] flex justify-between items-center px-[20px]">
   //                       <span className=" w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center text-[#FFFFFF80]">Commercial</span>
   //                       <input type="radio"/>
   //                    </div>
                   
   //                    <div className="w-full max-w-[255px] min-h-[42px] rounded-[4px] bg-[#00000033] flex justify-between items-center px-[20px]">
   //                       <span className=" w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center text-[#007B82]">Commercial</span>
   //                       <input type="radio"/>
   //                    </div>

   //                </div>
   //              </div>
              
   //         </div>
   //         </div>
   //       </div>

         
   //    </div>
       
   //     <div className="w-full max-w-[899px] min-h-[67px] rounded-[8px] border-[1px] border-solid border-[#FFFFFF4D] bg-gradient-to-l from-[#00B0BA] via-[#000000] to-[#007B82] flex justify-center items-center cursor-pointer">
   //        <div className="w-[200px] min-h-[35px] flex justify-center items-center gap-[10px] text-[20px] font-bold leading-[35px] spacing-[8px] text-center text-white"><span><img src={Magic} alt="magic" /></span>Generate Design</div>
          
   //     </div>
   //  </section>

   <section className="w-[full] max-w-[full] min-h-[1216px] px-[86px] py-[68px] flex flex-col justify-start items-center gap-[40px] bg-gradient-to-l from-[#002628] to-[#00646A]">
      <div className="max-w-[1268px] min-h-[113px]">
        <div className="max-w-[1268px] min-h-[67px] font-semibold text-[48px] leading-[140%] text-center text-white">
          Let AI Style It
        </div>
        <div className="max-w-[1268px] min-h-[34px] font-semibold text-[24px] leading-[140%] text-center text-white">
          Upload a photo to begin your AI-powered room design
        </div>
      </div>

      <div className="max-w-[1268px] min-h-[150px] flex flex-col items-center justify-start">
        <div className="max-w-[920px] min-h-[128px] flex justify-center items-center gap-[40px] flex-wrap">
          {tabs.map((tab) => (
            <div
              key={tab.name}
              className="w-[200px] h-[128px] flex flex-col justify-center items-center gap-[20px] cursor-pointer"
              onClick={() => {
                if (tab.name === "Upgrade to Unlock") {
                  alert("Please upgrade your account to access this feature");
                } else {
                  setActiveTab(tab.name);
                  setFormData((prev) => ({
                    ...prev,
                    roomType: "",
                    buildingType: "",
                  }));
                }
              }}
            >
              <div
                className={`w-[80px] h-[77px] border-[2px] px-[20px] py-[24px] flex justify-center items-center gap-[10px] rounded-[90px] transition-all duration-200 ${
                  activeTab === tab.name
                    ? "border-white bg-gradient-to-l from-[#00B0BA] via-[#000000] to-[#007B82]"
                    : "border-[#FFFFFF1A] bg-[#FFFFFF1A] hover:border-blue-300"
                }`}
              >
                <img src={tab.icon} alt={tab.name} />
              </div>
              <div className="max-w-[200px] min-h-[31px] text-[22px] font-semibold leading-[140%] text-center text-white">
                {tab.name}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="max-w-[1268px] min-h-[727px] flex flex-col justify-start items-center gap-[56px]">
        <form
          onSubmit={handleSubmit}
          className="max-w-[1268px] min-h-[604px] flex justify-between items-center gap-[82px] flex-wrap"
        >
          <div className="max-w-[636px] min-h-[604px] flex flex-col justify-center items-center gap-[12px]">
            <div
              className="w-[636px] min-h-[552px] rounded-[12px] border-[1px] border-dashed border-white flex justify-center items-center cursor-pointer"
              onClick={() => inpRef.current.click()}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              {imgURL ? (
                <img
                  src={imgURL}
                  alt="Preview"
                  className="w-full h-full object-cover rounded-[12px]"
                />
              ) : (
                <div className="w-[280px] min-h-[133px] flex flex-col justify-center items-center">
                  <div className="w-[70px] h-[70px] rounded-[40px] px-[18px] py-[16px] rouned-[40px] bg-[#FFFFFF1A] flex justify-center items-center">
                    <img src={Galley} alt="gallery" />
                  </div>
                  <div className="w-[280px] h-[68px] font-[400] text-[24px] leading-[140%] text-center text-[#FFFFFFB2]">
                    Drag & drop or click to upload a photo
                  </div>
                </div>
              )}
              <input
                type="file"
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

          <div className="w-[550px] h-[604px] flex flex-col items-start justify-start gap-[52px]">
            <div className="w-[550px] min-h-[411px] flex flex-col items-center justify-start gap-[31px]">
              <div className="w-[550px] min-h-[81px] flex flex-col justify-start items-center gap-[12px]">
                <div className="w-[550px] min-h-[27px] font-[400] text-[19px] leading-[140%] text-white">
                  Choose Building Type
                </div>
                <div className="w-[100%] max-w-[550px] min-h-[42px] flex justify-between items-center">
                  <div
                    className={`w-full max-w-[255px] min-h-[42px] rounded-[4px] flex justify-between items-center px-[20px] cursor-pointer ${
                      formData.buildingType === "Commercial"
                        ? "bg-white"
                        : "bg-[#00000033]"
                    }`}
                    onClick={() => handleChange("Commercial", "buildingType")}
                  >
                    <span
                      className={`w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center ${
                        formData.buildingType === "Commercial"
                          ? "text-[#007B82]"
                          : "text-[#FFFFFF80]"
                      }`}
                    >
                      Commercial
                    </span>
                    <input
                      type="radio"
                      checked={formData.buildingType === "Commercial"}
                      onChange={() => {}}
                    />
                  </div>

                  <div
                    className={`w-full max-w-[255px] min-h-[42px] rounded-[4px] flex justify-between items-center px-[20px] cursor-pointer ${
                      formData.buildingType === "Residential"
                        ? "bg-white"
                        : "bg-[#00000033]"
                    }`}
                    onClick={() => handleChange("Residential", "buildingType")}
                  >
                    <span
                      className={`w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center ${
                        formData.buildingType === "Residential"
                          ? "text-[#007B82]"
                          : "text-[#FFFFFF80]"
                      }`}
                    >
                      Residential
                    </span>
                    <input
                      type="radio"
                      checked={formData.buildingType === "Residential"}
                      onChange={() => {}}
                    />
                  </div>
                </div>
              </div>

              <div className="w-[550px] min-h-[81px] flex flex-col justify-start items-start gap-[12px]">
                <div className="w-[550px] min-h-[27px] font-[400] text-[19px] leading-[140%] text-white">
                  Select Room Type
                </div>
                <div className="w-full max-w-[550px] min-h-[42px] rounded-[4px] bg-white flex justify-between items-center px-[20px]">
                  <select
                    name="roomType"
                    value={formData.roomType}
                    onChange={(e) => handleChange(e.target.value, "roomType")}
                    className="w-[510px] h-[42px] cursor-pointer text-[#007B82]"
                  >
                    <option value="">Select room type</option>
                    {roomTypes[activeTab]?.map((room) => (
                      <option key={room} value={room}>
                        {room}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="w-[550px] min-h-[81px] flex flex-col justify-start items-start gap-[12px]">
                <div className="w-[550px] min-h-[27px] font-[400] text-[19px] leading-[140%] text-white">
                  Pick a Style
                </div>
                <div className="w-full max-w-[550px] min-h-[42px] rounded-[4px] bg-white flex justify-between items-center px-[20px]">
                  <select
                    name="roomStyle"
                    value={formData.roomStyle}
                    onChange={(e) => handleChange(e.target.value, "roomStyle")}
                    className="w-[510px] h-[42px] cursor-pointer text-[#007B82]"
                  >
                    <option value="">Select style</option>
                    {styles.map((style) => (
                      <option key={style} value={style}>
                        {style}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="w-[550px] min-h-[81px] flex flex-col justify-start items-start gap-[12px]">
                <div className="w-[550px] min-h-[27px] font-[400] text-[19px] leading-[140%] text-white">
                  Number of designs
                </div>
                <div className="w-full max-w-[550px] min-h-[42px] rounded-[4px] bg-white flex justify-between items-center px-[20px]">
                  <select
                    name="noOfDesign"
                    value={formData.noOfDesign}
                    onChange={(e) => handleChange(e.target.value, "noOfDesign")}
                    className="w-[510px] h-[42px] cursor-pointer text-[#007B82]"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => (
                      <option key={num} value={num}>
                        {num}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="w-full max-w-[550px] min-h-[141px] flex flex-col justify-start items-start gap-[12px]">
              <div className="w-[550px] min-h-[81px] flex flex-col justify-start items-start gap-[12px]">
                <div className="w-[550px] min-h-[27px] font-[400] text-[19px] leading-[140%] text-white">
                  AI Styling Strength
                </div>
                <div className="w-[100%] max-w-[550px] min-h-[42px] flex justify-between items-center">
                  <div
                    className={`w-full max-w-[255px] min-h-[42px] rounded-[4px] flex justify-between items-center px-[20px] cursor-pointer ${
                      formData.aiTouch === "Very Low" ? "bg-white" : "bg-[#00000033]"
                    }`}
                    onClick={() => handleChange("Very Low", "aiTouch")}
                  >
                    <span
                      className={`w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center ${
                        formData.aiTouch === "Very Low"
                          ? "text-[#007B82]"
                          : "text-[#FFFFFF80]"
                      }`}
                    >
                      Very Low
                    </span>
                    <input
                      type="radio"
                      checked={formData.aiTouch === "Very Low"}
                      onChange={() => {}}
                    />
                  </div>

                  <div
                    className={`w-full max-w-[255px] min-h-[42px] rounded-[4px] flex justify-between items-center px-[20px] cursor-pointer ${
                      formData.aiTouch === "Low" ? "bg-white" : "bg-[#00000033]"
                    }`}
                    onClick={() => handleChange("Low", "aiTouch")}
                  >
                    <span
                      className={`w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center ${
                        formData.aiTouch === "Low"
                          ? "text-[#007B82]"
                          : "text-[#FFFFFF80]"
                      }`}
                    >
                      Low
                    </span>
                    <input
                      type="radio"
                      checked={formData.aiTouch === "Low"}
                      onChange={() => {}}
                    />
                  </div>
                </div>
                <div className="w-[100%] max-w-[550px] min-h-[42px] flex justify-between items-center">
                  <div
                    className={`w-full max-w-[255px] min-h-[42px] rounded-[4px] flex justify-between items-center px-[20px] cursor-pointer ${
                      formData.aiTouch === "Medium" ? "bg-white" : "bg-[#00000033]"
                    }`}
                    onClick={() => handleChange("Medium", "aiTouch")}
                  >
                    <span
                      className={`w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center ${
                        formData.aiTouch === "Medium"
                          ? "text-[#007B82]"
                          : "text-[#FFFFFF80]"
                      }`}
                    >
                      Medium
                    </span>
                    <input
                      type="radio"
                      checked={formData.aiTouch === "Medium"}
                      onChange={() => {}}
                    />
                  </div>

                  <div
                    className={`w-full max-w-[255px] min-h-[42px] rounded-[4px] flex justify-between items-center px-[20px] cursor-pointer ${
                      formData.aiTouch === "High" ? "bg-white" : "bg-[#00000033]"
                    }`}
                    onClick={() => handleChange("High", "aiTouch")}
                  >
                    <span
                      className={`w-[92px] min-h-[22px] font-medium text-[16px] leading-[140%] text-center ${
                        formData.aiTouch === "High"
                          ? "text-[#007B82]"
                          : "text-[#FFFFFF80]"
                      }`}
                    >
                      High
                    </span>
                    <input
                      type="radio"
                      checked={formData.aiTouch === "High"}
                      onChange={() => {}}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="w-full max-w-[899px] min-h-[67px] rounded-[8px] border-[1px] border-solid border-[#FFFFFF4D] bg-gradient-to-l from-[#00B0BA] via-[#000000] to-[#007B82] flex justify-center items-center cursor-pointer">
            <button
              type="submit"
              className="w-[200px] min-h-[35px] flex justify-center items-center gap-[10px] text-[20px] font-bold leading-[35px] spacing-[8px] text-center text-white"
            >
              <span>
                <img src={Magic} alt="magic" />
              </span>
              Generate Design
            </button>
          </div>
        </form>
      </div>
    </section>



  );
}
