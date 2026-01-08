/**
 * SnowSpot App
 *
 * Main application component with routing and React Query setup.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import { Header, Footer } from './components/common';
import { Home, ResortPage, ComparisonPage, AlertsPage } from './pages';

// Create a client with default options
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: how long until data is considered stale
      staleTime: 3 * 60 * 1000, // 3 minutes
      // Cache time: how long to keep unused data in cache
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      // Retry failed requests up to 3 times
      retry: 3,
      // Refetch on window focus for fresh data
      refetchOnWindowFocus: true,
      // Don't refetch on reconnect by default
      refetchOnReconnect: 'always',
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/resort/:slug" element={<ResortPage />} />
              <Route path="/compare" element={<ComparisonPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
      {/* React Query Devtools - only in development */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
