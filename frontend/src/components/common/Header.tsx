/**
 * Header Component
 *
 * Main navigation header for the application.
 */

import { Link, NavLink } from 'react-router-dom';
import { FiHome, FiGrid, FiBell } from 'react-icons/fi';

export default function Header() {
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
      isActive
        ? 'text-blue-600 bg-blue-50'
        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
    }`;

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">S</span>
            </div>
            <span className="text-xl font-bold text-gray-900">SnowSpot</span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-2">
            <NavLink to="/" className={navLinkClass}>
              <FiHome className="mr-2" size={16} />
              Dashboard
            </NavLink>
            <NavLink to="/compare" className={navLinkClass}>
              <FiGrid className="mr-2" size={16} />
              Compare
            </NavLink>
            <NavLink to="/alerts" className={navLinkClass}>
              <FiBell className="mr-2" size={16} />
              Alerts
            </NavLink>
          </nav>
        </div>
      </div>
    </header>
  );
}
