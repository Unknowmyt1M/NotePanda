"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Search, 
  BookOpen, 
  FileText, 
  Folder, 
  ExternalLink, 
  Download, 
  ChevronRight, 
  Sparkles, 
  ShieldCheck, 
  X, 
  GraduationCap,
  Layers,
  ArrowLeft,
  Eye,
  CheckCircle2,
  Clock
} from 'lucide-react';
import dataSnapshot from '@/data_snapshot.json';

interface Batch {
  id: string;
  section: string;
  title: string;
  url: string;
  indexed_resources?: number;
  indexed_pdfs?: number;
}

interface FolderItem {
  id: string;
  batch_id: string;
  parent_id: string;
  title: string;
  depth: number;
  pdf_count: number;
}

interface Resource {
  id: string;
  batch_id: string;
  folder_id: string;
  title: string;
  file_url: string;
  is_pdf: number;
  created_at?: number;
  folder_title?: string;
  batch_title?: string;
}

export default function HomePage() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<Batch | null>(null);
  const [breadcrumbs, setBreadcrumbs] = useState<{ id: string; title: string }[]>([]);
  const [currentFolderId, setCurrentFolderId] = useState<string>("0");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [previewPdf, setPreviewPdf] = useState<{ url: string; title: string } | null>(null);

  // Initialize batches with statistics (Strictly PDF notes only)
  useEffect(() => {
    const rawBatches = dataSnapshot.batches.map((b: any) => {
      const pdfs = dataSnapshot.resources.filter((r: any) => r.batch_id === b.id && r.is_pdf === 1).length;
      return {
        ...b,
        indexed_resources: pdfs,
        indexed_pdfs: pdfs,
      };
    });
    setBatches(rawBatches);
    if (rawBatches.length > 0) {
      setSelectedBatch(rawBatches[0]);
    }
  }, []);

  // Compute subfolders under the currently active folder
  const currentSubfolders = useMemo(() => {
    if (!selectedBatch) return [];
    return dataSnapshot.folders.filter(
      (f: any) => f.batch_id === selectedBatch.id && f.parent_id === currentFolderId
    );
  }, [selectedBatch, currentFolderId]);

  // Compute PDF resources directly under current folder (Strictly PDFs only)
  const currentResources = useMemo(() => {
    if (!selectedBatch || currentFolderId === "0") return [];
    return dataSnapshot.resources.filter(
      (r: any) => r.batch_id === selectedBatch.id && r.folder_id === currentFolderId && r.is_pdf === 1
    );
  }, [selectedBatch, currentFolderId]);

  // Global search results across all batches and folders (Strictly PDFs)
  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase().trim();
    return dataSnapshot.resources
      .filter((r: any) => r.is_pdf === 1 && r.title.toLowerCase().includes(q))
      .slice(0, 40)
      .map((r: any) => {
        const folder = dataSnapshot.folders.find((f: any) => f.id === r.folder_id);
        const batch = dataSnapshot.batches.find((b: any) => b.id === r.batch_id);
        return {
          ...r,
          folder_title: folder ? folder.title : 'General',
          batch_title: batch ? batch.title : 'Study Batch',
        };
      });
  }, [searchQuery]);

  // Navigation handlers
  const handleSelectBatch = (batch: Batch) => {
    setSelectedBatch(batch);
    setCurrentFolderId("0");
    setBreadcrumbs([]);
  };

  const handleOpenFolder = (folder: FolderItem) => {
    setCurrentFolderId(folder.id);
    setBreadcrumbs(prev => [...prev, { id: folder.id, title: folder.title }]);
  };

  const handleNavigateBreadcrumb = (index: number) => {
    if (index === -1) {
      setCurrentFolderId("0");
      setBreadcrumbs([]);
    } else {
      const target = breadcrumbs[index];
      setCurrentFolderId(target.id);
      setBreadcrumbs(breadcrumbs.slice(0, index + 1));
    }
  };

  const totalPdfs = useMemo(() => {
    return dataSnapshot.resources.filter((r: any) => r.is_pdf === 1).length;
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14] text-gray-100">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-[#080c14]/80 border-b border-gray-800/80 px-4 sm:px-8 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => handleNavigateBreadcrumb(-1)}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <span className="text-xl">🐼</span>
          </div>
          <div>
            <h1 className="text-lg sm:text-xl font-bold tracking-tight bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
              NotePanda
            </h1>
            <p className="text-[10px] sm:text-xs text-emerald-400 font-medium">Free JEE & NEET PDF Notes Hub</p>
          </div>
        </div>

        {/* Global Live Stats Counter */}
        <div className="hidden md:flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{totalPdfs.toLocaleString()}+ Verified PDF Notes</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Direct CDN Access</span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10 space-y-8">
        {/* Hero & Search Section */}
        <div className="text-center max-w-3xl mx-auto space-y-4 pt-2 pb-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Sparkles className="w-3.5 h-3.5" /> Handpicked JEE & NEET Chapter Notes, DPPs & Formula Sheets
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Stop searching. <span className="bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">Start studying.</span>
          </h2>
          <p className="text-sm sm:text-base text-gray-400">
            Instant search across chapter revision notes, formula sheets, DPPs and question modules. Direct in-browser viewing with zero ads or logins.
          </p>

          {/* Interactive Search Bar */}
          <div className="relative max-w-2xl mx-auto mt-6">
            <div className="relative flex items-center">
              <Search className="absolute left-4 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search notes (e.g. Work Power Energy, Binomial Theorem, Structure of Atom, Mole Concept)..."
                className="w-full pl-12 pr-10 py-3.5 bg-gray-900/90 border border-gray-700/80 rounded-2xl text-sm sm:text-base text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all shadow-xl"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-4 text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Global Search Results View */}
        {searchQuery.trim().length > 0 ? (
          <div className="space-y-4 bg-gray-900/50 p-6 rounded-2xl border border-gray-800">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Search className="w-5 h-5 text-emerald-400" />
                Search Results for &quot;{searchQuery}&quot;
              </h3>
              <span className="text-xs text-gray-400">{searchResults.length} notes found</span>
            </div>

            {searchResults.length === 0 ? (
              <div className="py-12 text-center text-gray-500">
                <BookOpen className="w-10 h-10 mx-auto mb-2 opacity-50" />
                <p>No matching notes found. Try checking for chapter keywords like &quot;Kinematics&quot;, &quot;Formula&quot;, or &quot;Math&quot;.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                {searchResults.map((res: any) => (
                  <div
                    key={res.id}
                    className="p-4 rounded-xl bg-gray-800/60 border border-gray-700/60 hover:border-emerald-500/50 transition-all flex items-start justify-between gap-4 group"
                  >
                    <div className="space-y-1 truncate">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
                          PDF NOTE
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {res.folder_title}
                        </span>
                        <span className="text-xs text-gray-400 truncate max-w-[140px]">{res.batch_title}</span>
                      </div>
                      <h4 className="font-semibold text-sm sm:text-base text-gray-200 group-hover:text-emerald-300 transition-colors line-clamp-2">
                        {res.title}
                      </h4>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() => setPreviewPdf({ url: res.file_url, title: res.title })}
                        className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-1.5 transition-colors border border-emerald-500/30"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        Preview
                      </button>
                      <a
                        href={res.file_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 rounded-lg bg-gray-700/50 hover:bg-gray-700 text-gray-300 transition-colors"
                        title="Open / Download original PDF"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          /* Normal Browse / Tree Explorer View */
          <div className="space-y-6">
            {/* Batch Selector Tabs */}
            <div className="flex flex-wrap items-center gap-2 pb-2 border-b border-gray-800">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider mr-2 flex items-center gap-1">
                <GraduationCap className="w-4 h-4 text-emerald-400" /> Select Batch:
              </span>
              {batches.map((b) => (
                <button
                  key={b.id}
                  onClick={() => handleSelectBatch(b)}
                  className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center gap-2 ${
                    selectedBatch?.id === b.id
                      ? 'bg-emerald-500 text-gray-950 shadow-lg shadow-emerald-500/25 scale-[1.02]'
                      : 'bg-gray-900/80 text-gray-400 hover:text-gray-200 hover:bg-gray-800 border border-gray-800'
                  }`}
                >
                  <span>{b.title}</span>
                  {b.indexed_pdfs !== undefined && (
                    <span className={`px-2 py-0.5 rounded-full text-[10px] ${
                      selectedBatch?.id === b.id ? 'bg-gray-900/30 text-gray-950 font-bold' : 'bg-gray-800 text-emerald-400'
                    }`}>
                      {b.indexed_pdfs} Notes
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Breadcrumb Navigation Trail */}
            <nav className="flex items-center flex-wrap gap-2 text-xs sm:text-sm text-gray-400 bg-gray-900/40 px-4 py-2.5 rounded-xl border border-gray-800/60">
              <button
                onClick={() => handleNavigateBreadcrumb(-1)}
                className={`hover:text-emerald-400 transition-colors flex items-center gap-1 font-semibold ${
                  breadcrumbs.length === 0 ? 'text-emerald-400' : 'text-gray-300'
                }`}
              >
                <Layers className="w-4 h-4" />
                <span>{selectedBatch?.title || 'Subjects'}</span>
              </button>

              {breadcrumbs.map((crumb, idx) => (
                <React.Fragment key={crumb.id}>
                  <ChevronRight className="w-3.5 h-3.5 text-gray-600" />
                  <button
                    onClick={() => handleNavigateBreadcrumb(idx)}
                    className={`hover:text-emerald-400 transition-colors font-medium truncate max-w-[200px] ${
                      idx === breadcrumbs.length - 1 ? 'text-emerald-400 font-bold' : 'text-gray-400'
                    }`}
                  >
                    {crumb.title}
                  </button>
                </React.Fragment>
              ))}

              {breadcrumbs.length > 0 && (
                <button
                  onClick={() => handleNavigateBreadcrumb(breadcrumbs.length - 2)}
                  className="ml-auto text-xs text-gray-400 hover:text-white flex items-center gap-1 bg-gray-800/80 hover:bg-gray-800 px-2.5 py-1 rounded-lg border border-gray-700/50 transition-colors"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Back
                </button>
              )}
            </nav>

            {/* Subfolders Grid */}
            {currentSubfolders.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Folder className="w-4 h-4 text-amber-400" />
                  {currentFolderId === "0" ? "Subjects & Categories" : "Subfolders & Chapters"}
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
                  {currentSubfolders.map((folder: any) => (
                    <div
                      key={folder.id}
                      onClick={() => handleOpenFolder(folder)}
                      className="p-4 rounded-xl bg-gray-900/60 hover:bg-gray-800/80 border border-gray-800 hover:border-emerald-500/40 cursor-pointer transition-all duration-200 group flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3 truncate">
                        <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400 group-hover:bg-emerald-500/10 group-hover:text-emerald-400 transition-colors shrink-0">
                          <Folder className="w-5 h-5" />
                        </div>
                        <div className="truncate">
                          <h5 className="font-semibold text-sm sm:text-base text-gray-200 group-hover:text-white truncate">
                            {folder.title}
                          </h5>
                          <p className="text-xs text-emerald-400/80 font-medium mt-0.5">
                            {folder.pdf_count > 0 ? `${folder.pdf_count} PDF Notes` : 'Open Folder'}
                          </p>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all shrink-0" />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Direct Files / Resources Grid (Notes & Documents only) */}
            {currentResources.length > 0 && (
              <div className="space-y-3 pt-2">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-emerald-400" /> PDF Notes & Documents ({currentResources.length})
                </h4>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {currentResources.map((res: any) => (
                    <div
                      key={res.id}
                      className="p-4 rounded-xl bg-gray-900/90 border border-gray-800/90 hover:border-emerald-500/50 transition-all flex items-center justify-between gap-3 group"
                    >
                      <div className="flex items-start gap-3 truncate">
                        <div className="p-2 rounded-lg shrink-0 mt-0.5 bg-red-500/10 text-red-400 border border-red-500/20">
                          <FileText className="w-4 h-4" />
                        </div>
                        <div className="truncate">
                          <h5 className="font-semibold text-sm text-gray-200 group-hover:text-emerald-300 transition-colors truncate">
                            {res.title}
                          </h5>
                          <span className="text-[11px] text-gray-400 flex items-center gap-1 mt-0.5">
                            <Clock className="w-3 h-3" /> Direct CloudFront CDN
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <button
                          onClick={() => setPreviewPdf({ url: res.file_url, title: res.title })}
                          className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-1.5 transition-colors border border-emerald-500/30"
                        >
                          <Eye className="w-3.5 h-3.5" /> Preview
                        </button>
                        <a
                          href={res.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
                          title="Download PDF"
                        >
                          <Download className="w-4 h-4" />
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Empty Folder Notice */}
            {currentSubfolders.length === 0 && currentResources.length === 0 && (
              <div className="py-16 text-center text-gray-500 bg-gray-900/30 rounded-2xl border border-gray-800/50">
                <Folder className="w-12 h-12 mx-auto mb-3 opacity-40 text-gray-400" />
                <h5 className="text-base font-semibold text-gray-300">No notes in this folder</h5>
                <p className="text-xs text-gray-400 mt-1">Browse other subjects or check other batches in the top selector.</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Modern In-Browser PDF Preview Modal */}
      {previewPdf && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#0f172a] border border-gray-800 w-full max-w-5xl h-[92vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="px-4 py-3 bg-gray-900/90 border-b border-gray-800 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 truncate">
                <div className="p-1.5 rounded-md bg-red-500/20 text-red-400">
                  <FileText className="w-4 h-4" />
                </div>
                <h3 className="font-semibold text-sm sm:text-base text-gray-100 truncate">
                  {previewPdf.title}
                </h3>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <a
                  href={previewPdf.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 rounded-lg bg-emerald-500 text-gray-950 font-semibold text-xs flex items-center gap-1.5 hover:bg-emerald-400 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" /> Download PDF
                </a>
                <a
                  href={previewPdf.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
                  title="Open in new window"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
                <button
                  onClick={() => setPreviewPdf(null)}
                  className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Embedded Native / Iframe PDF Viewer */}
            <div className="flex-1 bg-gray-950 relative">
              <iframe
                src={`${previewPdf.url}#toolbar=0`}
                className="w-full h-full border-0"
                title={previewPdf.title}
              />
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-gray-800/80 bg-[#060910] py-8 px-4 text-center text-xs text-gray-500 space-y-2 mt-auto">
        <p className="font-medium text-gray-400">
          NotePanda 🐼 — Educational PDF Notes Discovery Engine for Indian Students
        </p>
        <p className="max-w-2xl mx-auto text-gray-400">
          Disclaimer: NotePanda does not host or mirror any copyrighted files. All documents and links remain hosted on their original CDN providers. Built for fair-use academic discovery and search indexation.
        </p>
      </footer>
    </div>
  );
}
