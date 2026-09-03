import { Outlet, Link, useLocation } from 'react-router-dom';
import './ResearchLayout.css';

export function ResearchLayout() {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/research' },
    { name: 'Library', path: '/research/papers' },
    { name: 'Compare', path: '/research/compare' },
    { name: 'Chat', path: '/research/chat' },
  ];

  return (
    <div className="research-layout flex h-[calc(100vh-64px)] bg-gray-50">
      {/* Sidebar Navigation */}
      <nav className="w-64 bg-white border-r flex flex-col p-4">
        <h2 className="text-lg font-bold mb-6 text-gray-800">Research Assistant</h2>
        <ul className="space-y-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`block px-4 py-2 rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-blue-50 text-blue-700 font-medium' 
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 overflow-auto bg-gray-50">
        <Outlet />
      </main>
    </div>
  );
}
