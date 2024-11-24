// src/components/ui/Accordion.js
import React, { useState } from "react";

export function Footer() {
  return (
    <footer className="pt-8 pb-4 ">
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="space-y-2">
          <p className="font-semibold">Navigation</p>
          <div className="space-y-1">
            <a href="#" className="block text-gray-600">
              Home
            </a>
            <a href="#" className="block text-gray-600">
              About
            </a>
            <a href="#" className="block text-gray-600">
              Products
            </a>
            <a href="#" className="block text-gray-600">
              Contact
            </a>
          </div>
        </div>
        <div className="space-y-2">
          <p className="font-semibold">Resources</p>
          <div className="space-y-1">
            <a href="#" className="block text-gray-600">
              Blog
            </a>
            <a href="#" className="block text-gray-600">
              Events
            </a>
            <a href="#" className="block text-gray-600">
              Gallery
            </a>
            <a href="#" className="block text-gray-600">
              Support
            </a>
          </div>
        </div>
      </div>
      <div className="mt-8 text-center text-sm text-gray-600">
        © 2024 RiceFarming Pro. All rights reserved.
      </div>
    </footer>
  );
}
