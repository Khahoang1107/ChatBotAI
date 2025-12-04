import React, { useState, useEffect } from 'react';
import { ArrowLeft, Download, FileSpreadsheet, FileText, Filter, Search, Calendar, Eye, X } from 'lucide-react';

interface Invoice {
  id: number;
  invoice_code: string;
  date: string;
  buyer_name: string;
  seller_name: string;
  total_amount: string;
  total_amount_value: number;
  subtotal?: number;
  tax_amount?: number;
  tax_percentage?: number;
  currency?: string;
  buyer_address?: string;
  seller_address?: string;
  buyer_tax_id?: string;
  seller_tax_id?: string;
  invoice_type: string;
  items?: string;
  confidence: number;
  ocr_method?: string;
  filename?: string;
  status: string;
  processed_at: string;
  file_path?: string;
}

interface InvoiceManagementProps {
  onBack: () => void;
}

const InvoiceManagement: React.FC<InvoiceManagementProps> = ({ onBack }) => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedInvoices, setSelectedInvoices] = useState<number[]>([]);
  const [viewingImage, setViewingImage] = useState<string | null>(null);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/invoices', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setInvoices(data.invoices);
      }
    } catch (error) {
      console.error('Error fetching invoices:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredInvoices = invoices.filter(inv => {
    const matchesSearch = 
      inv.invoice_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inv.buyer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inv.seller_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterType === 'all' || inv.invoice_type === filterType;
    
    return matchesSearch && matchesFilter;
  });

  const handleSelectAll = () => {
    if (selectedInvoices.length === filteredInvoices.length) {
      setSelectedInvoices([]);
    } else {
      setSelectedInvoices(filteredInvoices.map(inv => inv.id));
    }
  };

  const handleSelectInvoice = (id: number) => {
    if (selectedInvoices.includes(id)) {
      setSelectedInvoices(selectedInvoices.filter(i => i !== id));
    } else {
      setSelectedInvoices([...selectedInvoices, id]);
    }
  };

  const exportToExcel = async () => {
    const exportData = (selectedInvoices.length > 0 
      ? filteredInvoices.filter(inv => selectedInvoices.includes(inv.id))
      : filteredInvoices
    );

    if (exportData.length === 0) {
      alert('Không có dữ liệu để xuất!');
      return;
    }

    // Create CSV format with all fields (Excel can open CSV)
    const headers = [
      'STT', 'Mã hóa đơn', 'Ngày', 'Loại hóa đơn',
      'Người bán', 'Địa chỉ người bán', 'MST người bán',
      'Người mua', 'Địa chỉ người mua', 'MST người mua',
      'Tiền trước thuế', 'Thuế VAT', '% Thuế', 'Tổng tiền', 'Đơn vị tiền',
      'Độ tin cậy', 'Phương thức OCR', 'Tên file gốc',
      'Trạng thái', 'Xử lý lúc'
    ];
    
    const rows = exportData.map((inv, index) => {
      // Parse items if exists
      let itemsText = '';
      if (inv.items) {
        try {
          const items = JSON.parse(inv.items);
          itemsText = items.map((item: any) => 
            `${item.name || 'N/A'} (SL: ${item.quantity || 0}, Giá: ${item.price || 0})`
          ).join('; ');
        } catch (e) {
          itemsText = inv.items;
        }
      }
      
      return [
        index + 1,
        inv.invoice_code || '',
        inv.date || '',
        inv.invoice_type === 'electricity' ? 'Hóa đơn điện' : 
        inv.invoice_type === 'momo_payment' ? 'Thanh toán MoMo' : 
        inv.invoice_type === 'general' ? 'Hóa đơn thông thường' : inv.invoice_type,
        inv.seller_name || '',
        inv.seller_address || '',
        inv.seller_tax_id || '',
        inv.buyer_name || '',
        inv.buyer_address || '',
        inv.buyer_tax_id || '',
        inv.subtotal || 0,
        inv.tax_amount || 0,
        inv.tax_percentage ? `${inv.tax_percentage}%` : '',
        inv.total_amount_value || 0,
        inv.currency || 'VND',
        `${(inv.confidence * 100).toFixed(1)}%`,
        inv.ocr_method === 'tesseract' ? 'OCR (Tesseract)' : 'Metadata',
        inv.filename || '',
        inv.status || '',
        inv.processed_at || ''
      ];
    });

    const csvContent = [
      '\uFEFF' + headers.join(','), // BOM for UTF-8
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `invoices_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const exportToPDF = async () => {
    alert('Chức năng xuất PDF đang được phát triển. Vui lòng sử dụng xuất Excel và chuyển đổi sang PDF.');
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'electricity': return '⚡';
      case 'momo_payment': return '💳';
      default: return '📄';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <button
                onClick={onBack}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">Quản lý hóa đơn</h1>
                <p className="text-gray-600">Xem và xuất báo cáo hóa đơn</p>
              </div>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={exportToExcel}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <FileSpreadsheet className="w-5 h-5" />
                Xuất Excel
              </button>
              <button
                onClick={exportToPDF}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <FileText className="w-5 h-5" />
                Xuất PDF
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Tìm kiếm theo mã, người mua, người bán..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Tất cả loại</option>
              <option value="electricity">Hóa đơn điện</option>
              <option value="momo_payment">MoMo</option>
              <option value="general">Thông thường</option>
            </select>
          </div>

          <div className="flex items-center justify-between text-sm text-gray-600">
            <div>
              Hiển thị <strong>{filteredInvoices.length}</strong> / {invoices.length} hóa đơn
              {selectedInvoices.length > 0 && (
                <span className="ml-2">
                  • Đã chọn: <strong>{selectedInvoices.length}</strong>
                </span>
              )}
            </div>
            <button
              onClick={() => setSelectedInvoices([])}
              className="text-blue-600 hover:text-blue-800"
            >
              Bỏ chọn tất cả
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Đang tải dữ liệu...</p>
            </div>
          ) : filteredInvoices.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-gray-600 text-lg">Không tìm thấy hóa đơn nào</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedInvoices.length === filteredInvoices.length}
                        onChange={handleSelectAll}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">STT</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mã hóa đơn</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ngày</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Người bán</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Người mua</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Số tiền</th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Icon</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Loại hóa đơn</th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Độ tin cậy</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Xử lý lúc</th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Xem ảnh</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredInvoices.map((invoice, index) => (
                    <tr 
                      key={invoice.id}
                      className={`hover:bg-gray-50 transition-colors ${
                        selectedInvoices.includes(invoice.id) ? 'bg-blue-50' : ''
                      }`}
                    >
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedInvoices.includes(invoice.id)}
                          onChange={() => handleSelectInvoice(invoice.id)}
                          className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{index + 1}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{invoice.invoice_code}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{invoice.date}</td>
                      <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">{invoice.seller_name}</td>
                      <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">{invoice.buyer_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm font-semibold text-gray-900">
                          {invoice.total_amount_value.toLocaleString('vi-VN')} VND
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-2xl" title={invoice.invoice_type}>
                          {getTypeIcon(invoice.invoice_type)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {invoice.invoice_type === 'electricity' ? 'Hóa đơn điện' : 
                         invoice.invoice_type === 'momo_payment' ? 'Thanh toán MoMo' : 
                         invoice.invoice_type === 'general' ? 'Hóa đơn thông thường' : 
                         invoice.invoice_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getConfidenceColor(invoice.confidence)}`}>
                          {(invoice.confidence * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{invoice.processed_at}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        {invoice.file_path ? (
                          <button
                            onClick={() => setViewingImage(invoice.file_path!)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Xem ảnh hóa đơn"
                          >
                            <Eye className="w-5 h-5" />
                          </button>
                        ) : (
                          <span className="text-gray-400 text-xs">Không có</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Summary */}
        {filteredInvoices.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Thống kê</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Tổng số hóa đơn</p>
                <p className="text-2xl font-bold text-blue-600">{filteredInvoices.length}</p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Tổng giá trị</p>
                <p className="text-2xl font-bold text-green-600">
                  {filteredInvoices.reduce((sum, inv) => sum + inv.total_amount_value, 0).toLocaleString('vi-VN')} VND
                </p>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Độ tin cậy TB</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {(filteredInvoices.reduce((sum, inv) => sum + inv.confidence, 0) / filteredInvoices.length * 100).toFixed(1)}%
                </p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Đã chọn</p>
                <p className="text-2xl font-bold text-purple-600">{selectedInvoices.length}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Image Modal */}
      {viewingImage && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setViewingImage(null)}
        >
          <div className="relative max-w-6xl max-h-[90vh] bg-white rounded-lg overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setViewingImage(null)}
              className="absolute top-4 right-4 z-10 p-2 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors"
            >
              <X className="w-6 h-6 text-gray-800" />
            </button>
            <div className="p-4">
              <img
                src={`/api/invoices/image/${viewingImage}`}
                alt="Invoice"
                className="max-w-full max-h-[80vh] object-contain mx-auto"
                onError={(e) => {
                  e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400"%3E%3Crect width="400" height="400" fill="%23f0f0f0"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="monospace" font-size="20" fill="%23999"%3EKhông tải được ảnh%3C/text%3E%3C/svg%3E';
                }}
              />
            </div>
            <div className="bg-gray-50 px-6 py-4 border-t">
              <p className="text-sm text-gray-600 text-center">
                Click bên ngoài hoặc nút ✕ để đóng
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InvoiceManagement;
