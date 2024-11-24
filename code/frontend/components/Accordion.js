// src/components/ui/Accordion.js
import React, { useState } from 'react';

export function Accordion({ title, children }) {
const [isOpen, setIsOpen] = useState(false);

return (
  <div className="border-b">
    <button
      className="w-full text-left p-4 font-semibold flex justify-between items-center"
      onClick={() => setIsOpen(!isOpen)}
    >
      {title}
      <span>{isOpen ? '-' : '+'}</span>
    </button>
    {isOpen && <div className="p-4 text-sm text-gray-600">{children}</div>}
  </div>
);
}