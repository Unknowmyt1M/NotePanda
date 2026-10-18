import { NextResponse } from 'next/server';
import dataSnapshot from '@/data_snapshot.json';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const q = searchParams.get('q')?.toLowerCase()?.trim() || '';
  const batchId = searchParams.get('batchId');
  const folderId = searchParams.get('folderId');
  const type = searchParams.get('type'); // 'batches', 'folders', 'resources', 'search', 'stats'

  // 1. Stats
  if (type === 'stats') {
    return NextResponse.json({
      batches: dataSnapshot.batches.length,
      folders: dataSnapshot.folders.length,
      resources: dataSnapshot.resources.length,
      pdf_notes: dataSnapshot.resources.filter((r: any) => r.is_pdf === 1).length,
    });
  }

  // 2. Batches
  if (type === 'batches') {
    const batches = dataSnapshot.batches.map((b: any) => {
      const batchResources = dataSnapshot.resources.filter((r: any) => r.batch_id === b.id);
      const pdfCount = batchResources.filter((r: any) => r.is_pdf === 1).length;
      return {
        ...b,
        indexed_resources: batchResources.length,
        indexed_pdfs: pdfCount,
      };
    });
    return NextResponse.json({ batches });
  }

  // 3. Folders
  if (type === 'folders') {
    const targetParent = folderId || '0';
    const subfolders = dataSnapshot.folders.filter((f: any) => {
      const matchBatch = batchId ? f.batch_id === batchId : true;
      return matchBatch && f.parent_id === targetParent;
    });
    return NextResponse.json({ folders: subfolders });
  }

  // 4. Resources under a folder
  if (type === 'resources') {
    if (!folderId) {
      return NextResponse.json({ error: 'folderId required' }, { status: 400 });
    }
    const files = dataSnapshot.resources.filter((r: any) => r.folder_id === folderId);
    return NextResponse.json({ resources: files });
  }

  // 5. Global Search
  if (q) {
    const matches = dataSnapshot.resources
      .filter((r: any) => {
        const titleMatch = r.title.toLowerCase().includes(q);
        const isPdfMatch = r.is_pdf === 1;
        return titleMatch && isPdfMatch;
      })
      .slice(0, 50)
      .map((r: any) => {
        const folder = dataSnapshot.folders.find((f: any) => f.id === r.folder_id);
        const batch = dataSnapshot.batches.find((b: any) => b.id === r.batch_id);
        return {
          ...r,
          folder_title: folder ? folder.title : '',
          batch_title: batch ? batch.title : '',
        };
      });

    return NextResponse.json({ query: q, results: matches, count: matches.length });
  }

  // Default: Return batches and overall stats
  return NextResponse.json({
    status: 'ok',
    batches: dataSnapshot.batches,
    total_resources: dataSnapshot.resources.length,
  });
}
