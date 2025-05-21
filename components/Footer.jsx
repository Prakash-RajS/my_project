import React from "react";
import logo from "../assets/Logo.png";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faFacebookF,
  faTwitter,
  faInstagram,
  faPinterestP,
} from "@fortawesome/free-brands-svg-icons";
export default function Footer() {
  return (
    <footer className="w-full h-auto bg-white flex justify-center items-center flex-col mt-20 shadow-lg bg-[rgba(0,123,130,0.04)]">
      {/* <div className="w-full h-[2px] border-black bg-[#2a2a2a] rounded-[2px] mb-14"></div> */}
      <div className="max-w-full mx-auto grid lg:grid-cols-4 md:grid-cols-2 lg:mx-20 md:mx-12 sm:mx-10 sm:mx-0 gap-10 mt-10">
        <div className="mr-5">
          <img src={logo} alt="Stackly Logo" className="mb-4 w-32" />
          <p className="text-[16px] leading-[24px]">
            Automatically generate photo-like images of your desired spaces in
            seconds. Unleash the most advanced AI interior design tool to boost
            your productivity.
          </p>
          <div className="flex gap-4 mt-4">
            <a href="#" className="text-[#007b82]">
              <FontAwesomeIcon icon={faFacebookF} className="w-5 h-5" />
            </a>
            <a href="#" className="text-[#007b82]">
              <FontAwesomeIcon icon={faTwitter} className="w-5 h-5" />
            </a>
            <a href="#" className="text-[#007b82]">
              <FontAwesomeIcon icon={faInstagram} className="w-5 h-5" />
            </a>
            <a href="#" className="text-[#007b82]">
              <FontAwesomeIcon icon={faPinterestP} className="w-5 h-5" />
            </a>
          </div>
        </div>

        <div>
          <h4 className="font-bold text-[18px] mb-4 text-[#007b82]">
            Quick links
          </h4>
          <ul className=" text-[16px] leading-[40px] spacing-[0.3px] text-[#2A2A2A]">
            <li>
              <a href="#">Home</a>
            </li>
            <li>
              <a href="#">Trends</a>
            </li>
            <li>
              <a href="#">Products</a>
            </li>
            <li>
              <a href="#">Pricing</a>
            </li>
            <li>
              <a href="#">API</a>
            </li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-[18px] mb-4 text-[#007b82]">
            Terms & Policy
          </h4>
          <ul className="text-[16px] leading-[40px] spacing-[0.3px] text-[#2A2A2A]">
            <li>
              <a href="#">Terms of Services</a>
            </li>
            <li>
              <a href="#">Privacy and Cookie Policy</a>
            </li>
            <li>
              <a href="#">Cookie Settings</a>
            </li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-[18px] mb-4 text-[#007b82]">
            Contact Us
          </h4>
          <div className="text-[16px] leading-[40px] spacing-[0.3px] text-[#2A2A2A]">
            <a
              href="mailto:info@stacklyai.com"
              className="flex items-center gap-2 text-[#007B82] transition-colors"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
              <div className="text-[#2b2b2b]">info@stacklyai.com</div>
            </a>
          </div>
        </div>
      </div>

      <div className="w-[1300px] h-[2px] flex justify-center items-center bg-[#007B8233] sm:m-5 m-10"></div>

      <div className="text-center text-[#007B82] text-[16px] leading-[16px] tracking-[0.26px] text-xs mt-4 mb-10">
        &copy; 2023 Stackly AI | All Rights Reserved
      </div>
    </footer>
  );
}
