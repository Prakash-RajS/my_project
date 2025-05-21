import React, { useContext, useState } from "react";
import logoImg from "../assets/Logo.png";
import { NavLink, useNavigate } from "react-router-dom";
import { UserContext } from "../context/UserContext";

export default function Header() {
  const navigate = useNavigate();
  const [showSideBar, setShowSideBar] = useState(false);

  const { userInfo, setUserInfo } = useContext(UserContext);

  return (
    <div>
      <header className="w-full  h-[70px] sm:h-[90px] bg-white flex justify-between items-center backdrop-blur-[6px] xl:px-20 xl:py-[25px] md:p-[20px] p-[15px] relative z-10 gap-0 shadow-sm">
        <img
          className="cursor-pointer max-[400px]:w-[50%]"
          onClick={() => {
            navigate("/");
          }}
          src={logoImg}
          alt="Logo"
        />
        <nav>
          <ul
            className={`hidden gap-12 md:gap-8 min-[900px]:flex`}
            style={{ listStyle: "none" }}
          >
            <li>
              <NavLink
                className="text-[20px] font-bold text-[#2a2a2a] cursor-pointer no-underline leading-[100%] hover:text-[#007b82] NavLink visited:font-bold"
                to="/"
              >
                Home
              </NavLink>
            </li>
            <li>
              <NavLink
                className="text-[20px] font-bold text-[#2a2a2a] cursor-pointer no-underline leading-[100%] hover:text-[#007b82] NavLink visited:font-bold"
                to="/products"
              >
                Products
              </NavLink>
            </li>
            <li>
              <NavLink
                className="text-[20px] font-bold text-[#2a2a2a] cursor-pointer no-underline leading-[100%] hover:text-[#007b82] NavLink visited:font-bold"
                to="/pricing"
              >
                Pricing
              </NavLink>
            </li>
            <li>
              <NavLink
                className="text-[20px] font-bold text-[#2a2a2a] cursor-pointer no-underline leading-[100%] hover:text-[#007b82] NavLink visited:font-bold"
                to="/Api"
              >
                API
              </NavLink>
            </li>
            <li>
              <NavLink
                className="text-[20px] font-bold text-[#2a2a2a] cursor-pointer no-underline leading-[100%] hover:text-[#007b82] NavLink visited:font-bold"
                to="/contact"
              >
                Contact Us
              </NavLink>
            </li>
          </ul>
        </nav>
        <div className="flex items-center justify-center z-10 relative gap-5">
          {userInfo.userId ? (
            <div className="group z-10 relative cursor-pointer inline-flex items-center justify-center gap-1">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="32"
                height="32"
                viewBox="0 0 32 32"
                fill="none"
              >
                <g filter="url(#filter0_d_1339_1265)">
                  <path
                    d="M15.9919 14.6876C20.7011 14.6876 17.4032 14.5479 18.0584 14.2765C18.7136 14.0052 19.3089 13.6074 19.8103 13.106C20.3117 12.6045 20.7095 12.0092 20.9809 11.3541C21.2522 10.6989 21.3919 9.99674 21.3919 9.2876C21.3919 8.57846 21.2522 7.87627 20.9809 7.22111C20.7095 6.56595 20.3117 5.97066 19.8103 5.46922C19.3089 4.96779 18.7136 4.57003 18.0584 4.29865C17.4032 4.02728 20.7011 3.8876 15.9919 3.8876C14.5597 3.8876 13.1862 4.45653 12.1735 5.46922C11.2008 6.48192 10.5919 7.85543 10.5919 9.2876C10.5919 10.7198 11.2008 12.0933 12.1735 13.106C13.1862 14.1187 14.5597 14.6876 15.9919 14.6876ZM20.0003 2C17.581 1.99949 19.1179 2.51913 20.3739 3.47876C21.6299 4.43838 22.5352 5.78466 22.9501 7.30987C23.3651 8.83508 23.2666 10.4544 22.6699 11.9181C22.0732 13.3818 21.0114 14.6085 19.6483 15.4088C24.0739 20.7408 27.3979 20.4704 27.9943 25.1024C28.0507 25.5428 27.7231 25.9424 27.2623 25.9964C26.8027 26.0504 26.3827 25.7384 26.3263 25.298C25.6783 20.27 21.3235 20.484 20.0423 20.484C10.7323 20.484 6.32112 20.2772 5.67432 25.298C5.61792 25.7384 5.19792 26.0504 4.73832 25.9964C4.27752 25.9424 3.94992 25.5428 4.00632 25.1024C4.60152 20.4896 7.94352 20.7648 12.3763 15.4208C11.0091 14.6241 9.9425 13.3992 9.34132 11.9354C8.74014 10.4717 8.6379 8.85069 9.05042 7.32302C9.46293 5.79536 10.3672 4.44613 11.6235 3.48396C12.8797 2.52178 14.4179 2.00025 20.0003 2Z"
                    fill="#007B82"
                  />
                </g>
                <defs>
                  <filter
                    id="filter0_d_1339_1265"
                    x="0"
                    y="0"
                    width="32.001"
                    height="32.0025"
                    filterUnits="userSpaceOnUse"
                    colorInterpolationFilters="sRGB"
                  >
                    <feFlood floodOpacity="0" result="BackgroundImageFix" />
                    <feColorMatrix
                      in="SourceAlpha"
                      type="matrix"
                      values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
                      result="hardAlpha"
                    />
                    <feOffset dy="2" />
                    <feGaussianBlur stdDeviation="2" />
                    <feComposite in2="hardAlpha" operator="out" />
                    <feColorMatrix
                      type="matrix"
                      values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.1 0"
                    />
                    <feBlend
                      mode="normal"
                      in2="BackgroundImageFix"
                      result="effect1_dropShadow_1339_1265"
                    />
                    <feBlend
                      mode="normal"
                      in="SourceGraphic"
                      in2="effect1_dropShadow_1339_1265"
                      result="shape"
                    />
                  </filter>
                </defs>
              </svg>

              <svg
                className="group-hover:rotate-180 transition-all"
                xmlns="http://www.w3.org/2000/svg"
                width="13"
                height="8"
                viewBox="0 0 13 8"
                fill="none"
              >
                <path
                  d="M6.51543 1.86233L1.49227 6.88548C1.32142 7.05634 1.12209 7.13903 0.894278 7.13357C0.666471 7.1281 0.467138 7.03971 0.296283 6.8684C0.125427 6.69709 0.0399991 6.49776 0.0399991 6.2704C0.0399991 6.04305 0.125427 5.84372 0.296283 5.67241L5.54155 0.410054C5.67824 0.273369 5.83201 0.170856 6.00286 0.102514C6.17372 0.0341712 6.34458 7.93651e-08 6.51543 7.73277e-08C6.68629 7.52903e-08 6.85714 0.0341712 7.028 0.102514C7.19885 0.170856 7.35262 0.273369 7.48931 0.410054L12.7517 5.67241C12.9225 5.84327 13.0052 6.04556 12.9997 6.27929C12.9943 6.51302 12.9059 6.71508 12.7346 6.88548C12.5633 7.05588 12.3639 7.14131 12.1366 7.14177C11.9092 7.14222 11.7099 7.0568 11.5386 6.88548L6.51543 1.86233Z"
                  fill="#007B82"
                />
              </svg>

              <div
                className="profile-list min-w-[150px] p-4 z-10 hidden group-hover:flex flex-col gap-2 absolute bottom-0 right-0 bg-white rounded-md"
                style={{ transform: "translateY(95%)" }}
              >
                <NavLink>My Profile</NavLink>
                <NavLink>My Creations</NavLink>
                <p className="w-full h-[1px] bg-gray-600 my-1"></p>
                <NavLink
                  onClick={() => {
                    setUserInfo({});
                    navigate("/sign-in");
                  }}
                >
                  Logout
                </NavLink>
              </div>
            </div>
          ) : (
            <div className="min-[900px]:flex hidden  gap-[24px]">
              <NavLink
                to={"/sign-in"}
                className="w-[107px] h-[39px] text-[20px] font-semibold leading-[100%] border bg-white text-[#007b82] cursor-pointer flex justify-center items-center no-underline rounded-[5px] border-solid border-[#007b82]  active:bg-[#007b82] active:text-white"
              >
                Log In
              </NavLink>
              <NavLink
                to={"/sign-up"}
                className="w-[107px] h-[39px] text-[20px] font-semibold leading-[100%] border bg-[#007b82] text-white cursor-pointer flex justify-center items-center no-underline rounded-[5px] border-solid border-white active:bg-white active:text-[#007b82]"
              >
                Sign Up
              </NavLink>
            </div>
          )}

          <div
            onClick={() => {
              setShowSideBar(true);
            }}
            className={`hidden max-[900px]:block w-[30px] h-[30px]  cursor-pointer rounded-[5px]`}
          >
            <div className="w-full h-1 rounded-md bg-gray-700 transition-all duration-[0.3s] ease-[ease-in-out] mx-0 my-[5px]"></div>
            <div className="w-full h-1 rounded-md bg-gray-700 transition-all duration-[0.3s] ease-[ease-in-out] mx-0 my-[5px]"></div>
            <div className="w-full h-1 rounded-md bg-gray-700 transition-all duration-[0.3s] ease-[ease-in-out] mx-0 my-[5px]"></div>
          </div>
        </div>
      </header>

      <section
        className={`fixed top-0 ${
          showSideBar ? "right-0" : "right-[-200%]"
        } transition-all w-[70vw] sm:w-[50%] bg-white shadow-2xl min-h-[120vh] flex flex-col min-[900px]:hidden gap-7 justify-start items-start p-[40px] z-10`}
        style={{ listStyle: "none" }}
      >
        <svg
          onClick={() => {
            setShowSideBar(false);
          }}
          xmlns="http://www.w3.org/2000/svg"
          height="24px"
          viewBox="0 -960 960 960"
          width="24px"
          fill="#1f1f1f"
        >
          <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z" />
        </svg>
        <NavLink
          className="text-[20px] font-bold text-[#2a2a2a] cursor-pointer no-underline leading-[100%] hover:text-[#007b82] NavLink visited:font-bold"
          to="/"
          onClick={() => {
            setShowSideBar(false);
          }}
        >
          Home
        </NavLink>

        <NavLink
          className="text-[20px] font-bold text-[#2a2a2a] cursor-pointer no-underline leading-[100%] hover:text-[#007b82] NavLink visited:font-bold"
          to="/products"
          onClick={() => {
            setShowSideBar(false);
          }}
        >
          Products
        </NavLink>

        <NavLink
          className="text-[20px] font-bold text-[#2a2a2a] cursor-pointer no-underline leading-[100%] hover:text-[#007b82] NavLink visited:font-bold"
          to="/pricing"
          onClick={() => {
            setShowSideBar(false);
          }}
        >
          Pricing
        </NavLink>

        <NavLink
          className="text-[20px] font-bold text-[#2a2a2a] cursor-pointer no-underline leading-[100%] hover:text-[#007b82] NavLink visited:font-bold"
          to="/Api"
          onClick={() => {
            setShowSideBar(false);
          }}
        >
          API
        </NavLink>

        <NavLink
          className="text-[20px] font-bold text-[#2a2a2a] cursor-pointer no-underline leading-[100%] hover:text-[#007b82] NavLink visited:font-bold"
          to="/contact"
          onClick={() => {
            setShowSideBar(false);
          }}
        >
          Contact Us
        </NavLink>

        {!userInfo.userId && (
          <>
            <button
              className="w-[107px] h-[39px] text-[20px] font-semibold leading-[100%] border bg-white text-[#007b82] cursor-pointer flex justify-center items-center no-underline rounded-[5px] border-solid border-[#007b82] active:bg-[#007b82] active:text-white"
              onClick={() => {
                navigate("/sign-in");
                setShowSideBar(false);
              }}
            >
              Log In
            </button>
            <button
              className="w-[107px] h-[39px] text-[20px] font-semibold leading-[100%] border bg-[#007b82] text-white cursor-pointer flex justify-center items-center no-underline rounded-[5px] border-solid border-white active:bg-white active:text-[#007b82]"
              onClick={() => {
                navigate("/sign-up");
                setShowSideBar(false);
              }}
            >
              Sign Up
            </button>
          </>
        )}
      </section>
    </div>
  );
}
