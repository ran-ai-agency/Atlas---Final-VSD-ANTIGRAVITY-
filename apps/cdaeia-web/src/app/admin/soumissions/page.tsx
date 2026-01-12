'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Link from 'next/link';
import {
  Search,
  Filter,
  Download,
  Eye,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  SortAsc,
  SortDesc,
  CheckCircle,
  AlertTriangle,
  XCircle
} from 'lucide-react';

interface DiagnosticRecord {
  id: string;
  company_name: string;
  company_neq: string | null;
  email: string | null;
  total_score: number;
  max_score: number;
  percentage: number;
  eligibility_status: 'eligible' | 'partial' | 'not_eligible';
  credit_current: number | null;
  credit_optimized: number | null;
  credit_gain: number;
  created_at: string;
}

type SortField = 'company_name' | 'percentage' | 'credit_current' | 'created_at';
type SortOrder = 'asc' | 'desc';

const ITEMS_PER_PAGE = 10;

export default function SoumissionsPage() {
  const [diagnostics, setDiagnostics] = useState<DiagnosticRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [currentPage, setCurrentPage] = useState(1);

  const fetchDiagnostics = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/diagnostics');
      if (!response.ok) throw new Error('Erreur');
      const data = await response.json();
      setDiagnostics(data.diagnostics || []);
    } catch (err) {
      console.error('Error:', err);
      setDiagnostics([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
  }, []);

  // Filter and sort
  const filteredAndSorted = useMemo(() => {
    let result = [...diagnostics];

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(d =>
        d.company_name.toLowerCase().includes(term) ||
        d.company_neq?.toLowerCase().includes(term) ||
        d.email?.toLowerCase().includes(term)
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      result = result.filter(d => d.eligibility_status === statusFilter);
    }

    // Sort
    result.sort((a, b) => {
      let comparison = 0;
      switch (sortField) {
        case 'company_name':
          comparison = a.company_name.localeCompare(b.company_name);
          break;
        case 'percentage':
          comparison = a.percentage - b.percentage;
          break;
        case 'credit_current':
          comparison = (a.credit_current || 0) - (b.credit_current || 0);
          break;
        case 'created_at':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [diagnostics, searchTerm, statusFilter, sortField, sortOrder]);

  // Pagination
  const totalPages = Math.ceil(filteredAndSorted.length / ITEMS_PER_PAGE);
  const paginatedData = filteredAndSorted.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const exportCSV = () => {
    const headers = ['Entreprise', 'NEQ', 'Email', 'Score', 'Statut', 'Credit Actuel', 'Credit Optimise', 'Gain', 'Date'];
    const rows = filteredAndSorted.map(d => [
      d.company_name,
      d.company_neq || '',
      d.email || '',
      `${d.percentage}%`,
      d.eligibility_status,
      d.credit_current || 0,
      d.credit_optimized || 0,
      d.credit_gain,
      new Date(d.created_at).toLocaleDateString('fr-CA')
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cdaeia-diagnostics-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Soumissions</h1>
          <p className="text-gray-600">
            {filteredAndSorted.length} diagnostic{filteredAndSorted.length !== 1 ? 's' : ''} trouve{filteredAndSorted.length !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={fetchDiagnostics}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualiser
          </Button>
          <Button variant="outline" onClick={exportCSV}>
            <Download className="w-4 h-4 mr-2" />
            Exporter CSV
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <Input
                placeholder="Rechercher par nom, NEQ ou email..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Tous les statuts</option>
                <option value="eligible">Eligible</option>
                <option value="partial">Partiel</option>
                <option value="not_eligible">Non eligible</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="pt-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : paginatedData.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Filter className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Aucun diagnostic trouve</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left text-sm text-gray-500">
                      <th
                        className="pb-3 font-medium cursor-pointer hover:text-gray-900"
                        onClick={() => handleSort('company_name')}
                      >
                        <div className="flex items-center gap-2">
                          Entreprise
                          <SortIcon field="company_name" />
                        </div>
                      </th>
                      <th className="pb-3 font-medium">NEQ</th>
                      <th className="pb-3 font-medium">Statut</th>
                      <th
                        className="pb-3 font-medium cursor-pointer hover:text-gray-900"
                        onClick={() => handleSort('percentage')}
                      >
                        <div className="flex items-center gap-2">
                          Score
                          <SortIcon field="percentage" />
                        </div>
                      </th>
                      <th
                        className="pb-3 font-medium cursor-pointer hover:text-gray-900"
                        onClick={() => handleSort('credit_current')}
                      >
                        <div className="flex items-center gap-2">
                          Credit
                          <SortIcon field="credit_current" />
                        </div>
                      </th>
                      <th className="pb-3 font-medium">Gain Pot.</th>
                      <th
                        className="pb-3 font-medium cursor-pointer hover:text-gray-900"
                        onClick={() => handleSort('created_at')}
                      >
                        <div className="flex items-center gap-2">
                          Date
                          <SortIcon field="created_at" />
                        </div>
                      </th>
                      <th className="pb-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {paginatedData.map((diagnostic) => (
                      <tr key={diagnostic.id} className="hover:bg-gray-50">
                        <td className="py-4">
                          <div>
                            <div className="font-medium">{diagnostic.company_name}</div>
                            {diagnostic.email && (
                              <div className="text-sm text-gray-500">{diagnostic.email}</div>
                            )}
                          </div>
                        </td>
                        <td className="py-4 text-gray-600">
                          {diagnostic.company_neq || '-'}
                        </td>
                        <td className="py-4">
                          <StatusBadge status={diagnostic.eligibility_status} />
                        </td>
                        <td className="py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full ${
                                  diagnostic.percentage >= 80 ? 'bg-green-500' :
                                  diagnostic.percentage >= 50 ? 'bg-amber-500' : 'bg-red-500'
                                }`}
                                style={{ width: `${diagnostic.percentage}%` }}
                              />
                            </div>
                            <span className="text-sm font-medium">{diagnostic.percentage.toFixed(0)}%</span>
                          </div>
                        </td>
                        <td className="py-4 font-medium">
                          {diagnostic.credit_current
                            ? formatCurrency(diagnostic.credit_current)
                            : '-'}
                        </td>
                        <td className="py-4 text-green-600 font-medium">
                          {diagnostic.credit_gain > 0
                            ? `+${formatCurrency(diagnostic.credit_gain)}`
                            : '-'}
                        </td>
                        <td className="py-4 text-gray-500 text-sm">
                          {formatDate(diagnostic.created_at)}
                        </td>
                        <td className="py-4">
                          <Link href={`/admin/soumissions/${diagnostic.id}`}>
                            <Button variant="ghost" size="sm">
                              <Eye className="w-4 h-4 mr-1" />
                              Voir
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-6 pt-4 border-t">
                  <div className="text-sm text-gray-500">
                    Page {currentPage} sur {totalPages}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }
                      return (
                        <Button
                          key={pageNum}
                          variant={currentPage === pageNum ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setCurrentPage(pageNum)}
                        >
                          {pageNum}
                        </Button>
                      );
                    })}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; className: string; icon: React.ReactNode }> = {
    eligible: {
      label: 'Eligible',
      className: 'bg-green-100 text-green-700',
      icon: <CheckCircle className="w-3 h-3" />
    },
    partial: {
      label: 'Partiel',
      className: 'bg-amber-100 text-amber-700',
      icon: <AlertTriangle className="w-3 h-3" />
    },
    not_eligible: {
      label: 'Non eligible',
      className: 'bg-red-100 text-red-700',
      icon: <XCircle className="w-3 h-3" />
    }
  };

  const { label, className, icon } = config[status] || config.not_eligible;

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${className}`}>
      {icon}
      {label}
    </span>
  );
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('fr-CA', {
    style: 'currency',
    currency: 'CAD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('fr-CA', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}
