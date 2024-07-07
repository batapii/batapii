// File: DeveloperStatusCard.jsx

import React from 'react';
import { Shield } from 'lucide-react';

const SkillBar = ({ skill, level, maxLevel = 10 }) => (
  <div className="mb-2">
    <div className="flex justify-between mb-1">
      <span className="text-sm font-medium text-blue-700">{skill}</span>
      <span className="text-sm font-medium text-blue-700">{level}/{maxLevel}</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2.5">
      <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${(level / maxLevel) * 100}%` }}></div>
    </div>
  </div>
);

const DeveloperStatusCard = () => {
  const skills = [
    { name: 'Kotlin', level: 8 },
    { name: 'Android SDK', level: 7 },
    { name: 'Jetpack Compose', level: 6 },
    { name: 'MVVM Architecture', level: 7 },
    { name: 'Kotlin Coroutines', level: 6 },
  ];

  return (
    <div className="bg-white shadow-lg rounded-lg p-6 max-w-sm mx-auto">
      <div className="flex items-center mb-4">
        <Shield className="h-10 w-10 text-blue-500 mr-3" />
        <h2 className="text-2xl font-bold text-gray-800">Developer Stats</h2>
      </div>
      <div className="mb-4">
        <p className="text-gray-600"><strong>Class:</strong> Android Wizard</p>
        <p className="text-gray-600"><strong>Level:</strong> 42</p>
        <p className="text-gray-600"><strong>Experience:</strong> 5 years</p>
      </div>
      <div>
        <h3 className="text-xl font-semibold mb-2 text-gray-800">Skills</h3>
        {skills.map((skill, index) => (
          <SkillBar key={index} skill={skill.name} level={skill.level} />
        ))}
      </div>
      <div className="mt-4">
        <h3 className="text-xl font-semibold mb-2 text-gray-800">Special Abilities</h3>
        <ul className="list-disc list-inside text-gray-600">
          <li>Debugging Mastery</li>
          <li>UI/UX Intuition</li>
          <li>Performance Optimization</li>
        </ul>
      </div>
    </div>
  );
};

export default DeveloperStatusCard;
