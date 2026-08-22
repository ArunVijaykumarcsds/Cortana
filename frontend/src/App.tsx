import { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { MotionConfig } from "framer-motion";
import Landing from "./pages/Landing";
import AppLayout from "./layouts/AppLayout";

const CommandCenter = lazy(() => import("./pages/CommandCenter"));
const Transactions = lazy(() => import("./pages/Transactions"));
const TransactionDetail = lazy(() => import("./pages/TransactionDetail"));
const Alerts = lazy(() => import("./pages/Alerts"));
const Investigations = lazy(() => import("./pages/Investigations"));
const InvestigationDetail = lazy(() => import("./pages/InvestigationDetail"));
const ModelIntelligence = lazy(() => import("./pages/ModelIntelligence"));
const SystemPage = lazy(() => import("./pages/SystemPage"));

function RouteFallback() {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <span className="label-eyebrow">Loading…</span>
    </div>
  );
}

export default function App() {
  return (
    <MotionConfig reducedMotion="user">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/app" element={<AppLayout />}>
            <Route
              index
              element={
                <Suspense fallback={<RouteFallback />}>
                  <CommandCenter />
                </Suspense>
              }
            />
            <Route
              path="transactions"
              element={
                <Suspense fallback={<RouteFallback />}>
                  <Transactions />
                </Suspense>
              }
            />
            <Route
              path="transactions/:id"
              element={
                <Suspense fallback={<RouteFallback />}>
                  <TransactionDetail />
                </Suspense>
              }
            />
            <Route
              path="alerts"
              element={
                <Suspense fallback={<RouteFallback />}>
                  <Alerts />
                </Suspense>
              }
            />
            <Route
              path="investigations"
              element={
                <Suspense fallback={<RouteFallback />}>
                  <Investigations />
                </Suspense>
              }
            />
            <Route
              path="investigations/:id"
              element={
                <Suspense fallback={<RouteFallback />}>
                  <InvestigationDetail />
                </Suspense>
              }
            />
            <Route
              path="model-intelligence"
              element={
                <Suspense fallback={<RouteFallback />}>
                  <ModelIntelligence />
                </Suspense>
              }
            />
            <Route
              path="system"
              element={
                <Suspense fallback={<RouteFallback />}>
                  <SystemPage />
                </Suspense>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </MotionConfig>
  );
}
