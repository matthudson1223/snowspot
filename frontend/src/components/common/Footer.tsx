/**
 * Footer Component
 *
 * Simple footer with copyright and links.
 */

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between text-sm text-gray-600">
          <p>&copy; {currentYear} SnowSpot. All rights reserved.</p>
          <div className="flex items-center space-x-4 mt-2 md:mt-0">
            <a href="#" className="hover:text-gray-900 transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-gray-900 transition-colors">
              Terms of Service
            </a>
            <a href="#" className="hover:text-gray-900 transition-colors">
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
