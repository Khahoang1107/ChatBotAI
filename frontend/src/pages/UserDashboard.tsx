import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ProfileSettings } from './ProfileSettings';
import InvoiceManagement from './InvoiceManagement';
import { apiService } from '@/services/apiService';
import { 
  Bell, 
  LogOut, 
  Camera, 
  Upload, 
  Send, 
  User,
  FileText,
  X
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface UserDashboardProps {
  user: {
    email: string;
    name: string;
  };
  onLogout: () => void;
  onUpdateUser?: (name: string, email: string) => Promise<boolean>;
}

export function UserDashboard({ user, onLogout, onUpdateUser }: UserDashboardProps) {
  const [currentView, setCurrentView] = useState<'dashboard' | 'invoices'>('dashboard');
  const [messages, setMessages] = useState([
    { id: 1, text: '👋 Xin chào! Tôi là trợ lý AI của Invoice Manager.\n\n💡 Gõ "Chatbot có thể làm gì?" để xem tất cả chức năng tôi có thể giúp bạn!', sender: 'bot', time: '10:30' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showQuickSuggestions, setShowQuickSuggestions] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showSettings, setShowSettings] = useState(false);

  // Debug effect to monitor cameraActive state changes
  useEffect(() => {
    console.log('cameraActive state changed:', cameraActive);
  }, [cameraActive]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const addBotMessage = (text: string) => {
    const botTime = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    setMessages(prev => [...prev, 
      { id: prev.length + 1, text, sender: 'bot', time: botTime }
    ]);
    setTimeout(scrollToBottom, 100);
  };

  const handleQuickSuggestion = async (question: string) => {
    const currentTime = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    
    // Add user message
    setMessages(prev => [...prev, 
      { id: prev.length + 1, text: question, sender: 'user', time: currentTime }
    ]);
    
    // Send to chat API
    setIsTyping(true);
    
    try {
      const data = await apiService.sendChatMessage(question);
      
      setIsTyping(false);
      addBotMessage(data.response);
      
      // Show action buttons ONLY if asking about capabilities
      const isCapabilityQuestion = 
        (question.toLowerCase().includes('làm gì') || 
         question.toLowerCase().includes('chức năng') ||
         question.toLowerCase().includes('features') ||
         question.toLowerCase().includes('capabilities')) &&
        (question.toLowerCase().includes('có thể') ||
         question.toLowerCase().includes('bot') ||
         question.toLowerCase().includes('chatbot') ||
         question.toLowerCase().includes('hệ thống'));
      
      setShowQuickSuggestions(isCapabilityQuestion);
    } catch (error) {
      setIsTyping(false);
      addBotMessage('Xin lỗi, tôi gặp sự cố khi xử lý tin nhắn. Vui lòng thử lại.');
      console.error('Chat error:', error);
    }
  };
  
  const handleActionButton = async (action: string, params?: any) => {
    const currentTime = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    
    setMessages(prev => [...prev, 
      { id: prev.length + 1, text: action, sender: 'user', time: currentTime }
    ]);
    
    setIsTyping(true);
    
    try {
      const token = localStorage.getItem('token');
      
      if (action.includes('Xem danh sách')) {
        // Call invoices API
        const response = await fetch('/api/invoices', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
          const data = await response.json();
          const invoices = data.invoices;
          
          setIsTyping(false);
          
          if (invoices.length === 0) {
            addBotMessage('📋 **Danh sách hóa đơn**\n\n⚠️ Chưa có hóa đơn nào được xử lý.\n\n💡 Hãy upload hoặc chụp hóa đơn để bắt đầu!');
            return;
          }
          
          let message = `📋 **Danh sách hóa đơn**\n━━━━━━━━━━━━━━━━━━━━\nTổng số: ${invoices.length} hóa đơn\n\n`;
          
          invoices.forEach((inv: any, idx: number) => {
            const confidenceIcon = inv.confidence >= 0.8 ? '✅' : inv.confidence >= 0.6 ? '⚠️' : '❌';
            const typeIcon = inv.invoice_type === 'momo_payment' ? '💳' : inv.invoice_type === 'electricity' ? '⚡' : '📄';
            
            message += `【${idx + 1}】 **${inv.invoice_code}**\n`;
            message += `━━━━━━━━━━━━━━━━\n`;
            message += `${typeIcon} Loại: ${inv.invoice_type === 'momo_payment' ? 'MoMo' : inv.invoice_type === 'electricity' ? 'Hóa đơn điện' : 'Thông thường'}\n`;
            message += `📅 Ngày: ${inv.date}\n`;
            message += `🏢 Người bán:\n   ${inv.seller_name}\n`;
            message += `👤 Người mua:\n   ${inv.buyer_name}\n`;
            message += `💰 Tổng tiền:\n   ${inv.total_amount}\n`;
            message += `${confidenceIcon} Độ tin cậy: ${(inv.confidence * 100).toFixed(1)}%\n`;
            message += `⏰ Xử lý lúc: ${inv.processed_at}\n`;
            message += `\n`;
          });
          
          message += '━━━━━━━━━━━━━━━━━━━━\n';
          message += '💡 Gõ mã hóa đơn để xem chi tiết';
          
          addBotMessage(message);
        } else {
          throw new Error('Failed to fetch invoices');
        }
      } else if (action.includes('Tìm kiếm')) {
        setIsTyping(false);
        addBotMessage('🔍 **Tìm kiếm hóa đơn**\n\nVui lòng nhập mã hóa đơn bạn muốn tìm (ví dụ: INV-12345)');
      } else if (action.includes('Lọc theo ngày')) {
        setIsTyping(false);
        addBotMessage('📅 **Lọc hóa đơn theo ngày**\n\nVui lòng nhập khoảng thời gian (ví dụ: "hóa đơn trong tháng 11" hoặc "từ 01/11 đến 30/11")');
      } else if (action.includes('Xuất báo cáo')) {
        setIsTyping(false);
        addBotMessage('📊 **Đang chuyển đến trang quản lý hóa đơn...**\n\nTại đây bạn có thể:\n• Xem tất cả hóa đơn dạng bảng\n• Tìm kiếm và lọc\n• Xuất Excel hoặc PDF');
        
        setTimeout(() => {
          setCurrentView('invoices');
        }, 1000);
      } else if (action.includes('Thống kê')) {
        setIsTyping(false);
        addBotMessage('📈 **Thống kê hóa đơn**\n\n📊 Dữ liệu tổng quan:\n• Tổng hóa đơn: 5\n• Đã thanh toán: 2\n• Chờ xử lý: 2\n• Quá hạn: 1\n\n💰 Tổng doanh thu: 8,450,000 VNĐ\n📅 Trung bình: 1,690,000 VNĐ/hóa đơn');
      }
    } catch (error) {
      setIsTyping(false);
      addBotMessage('❌ Có lỗi xảy ra. Vui lòng thử lại.');
      console.error('Action error:', error);
    }
  };

  const handleChatCommand = async (command: string) => {
    const cmd = command.toLowerCase().trim();
    
    // View invoice list command
    if (cmd.includes('xem') && (cmd.includes('danh sách') || cmd.includes('hóa đơn'))) {
      await handleActionButton('📋 Xem danh sách hóa đơn');
      return true;
    }
    
    // Search invoice command
    if (cmd.includes('tìm') && cmd.includes('hóa đơn')) {
      await handleActionButton('🔍 Tìm kiếm hóa đơn');
      return true;
    }
    
    // Filter by date command
    if (cmd.includes('lọc') || (cmd.includes('hóa đơn') && (cmd.includes('ngày') || cmd.includes('tháng') || cmd.includes('hôm nay')))) {
      await handleActionButton('📅 Lọc theo ngày');
      return true;
    }
    
    // Export report command - redirect to invoice management page
    if (cmd.includes('xuất') && (cmd.includes('báo cáo') || cmd.includes('excel') || cmd.includes('pdf') || cmd.includes('file'))) {
      await handleActionButton('📊 Xuất báo cáo');
      return true;
    }
    
    // Direct "Quản lý hóa đơn" command
    if (cmd.includes('quản lý') && cmd.includes('hóa đơn')) {
      addBotMessage('📊 **Đang chuyển đến trang quản lý hóa đơn...**');
      setTimeout(() => {
        setCurrentView('invoices');
      }, 500);
      return true;
    }
    
    // Statistics command
    if (cmd.includes('thống kê') || cmd.includes('số liệu')) {
      await handleActionButton('📈 Thống kê');
      return true;
    }
    
    // Camera commands
    if (cmd.includes('mở camera') || cmd.includes('bật camera') || cmd.includes('chụp ảnh')) {
      if (!cameraActive) {
        await handleStartCamera();
        addBotMessage('📷 **Đã mở camera!**\n\nCamera đang hoạt động. Bạn có thể:\n• Gõ "chụp ảnh" để chụp\n• Gõ "đóng camera" để tắt\n• Gõ "xử lý" để xử lý hóa đơn');
      } else {
        addBotMessage('📷 Camera đang mở rồi! Gõ "chụp ảnh" hoặc "xử lý" để tiếp tục.');
      }
      return true;
    }
    
    if (cmd.includes('đóng camera') || cmd.includes('tắt camera')) {
      if (cameraActive) {
        handleStopCamera();
        addBotMessage('📷 **Đã đóng camera!**\n\n💡 Gõ "mở camera" để mở lại.');
      } else {
        addBotMessage('📷 Camera chưa được mở.');
      }
      return true;
    }
    
    if (cmd.includes('chụp') && cameraActive) {
      handleCapturePhoto();
      addBotMessage('📸 **Đã chụp ảnh!**\n\nẢnh đã được lưu. Gõ "xử lý" hoặc "xử lý hóa đơn" để phân tích.');
      return true;
    }
    
    // Process invoice command
    if (cmd.includes('xử lý') || cmd.includes('phân tích') || cmd.includes('ocr')) {
      if (uploadedFile || cameraActive) {
        await handleProcessInvoice();
        return true;
      } else {
        addBotMessage('⚠️ **Chưa có hóa đơn để xử lý!**\n\nVui lòng:\n• Gõ "mở camera" để chụp ảnh\n• Hoặc upload file từ nút bên trái');
        return true;
      }
    }
    
    // Upload file command
    if (cmd.includes('upload') || cmd.includes('tải lên')) {
      addBotMessage('📤 **Upload hóa đơn:**\n\nNhấn vào nút "Upload File" 📁 ở bên trái để chọn file hình ảnh hóa đơn từ máy tính.\n\nSau khi chọn file, gõ "xử lý" để phân tích!');
      return true;
    }
    
    return false;
  };

  const handleProcessInvoice = async () => {
    if (!uploadedFile && !cameraActive) return;
    
    setIsProcessing(true);
    const currentTime = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    
    // Add user message
    setMessages(prev => [...prev, 
      { id: prev.length + 1, text: `Xử lý hóa đơn: ${uploadedFile?.name || 'Ảnh từ camera'}`, sender: 'user', time: currentTime }
    ]);
    
    setIsTyping(true);
    
    try {
      // Call real backend API using apiService
      if (!uploadedFile) {
        throw new Error('No file uploaded');
      }
      
      const data = await apiService.uploadInvoice(uploadedFile);
      
      // Check response format and extract invoice data
      const invoice = data.data?.extracted_data || data.invoice || data.data;
      
      if (!invoice) {
        throw new Error('No invoice data returned from server');
      }
      
      setIsTyping(false);
      
      // Bot response with invoice analysis
      addBotMessage('🔍 Đang phân tích hóa đơn...');
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const confidence = (invoice.confidence * 100).toFixed(1);
      const confidenceIcon = invoice.confidence >= 0.8 ? '✅' : invoice.confidence >= 0.6 ? '⚠️' : '❌';
      
      let message = `${confidenceIcon} Đã xử lý hóa đơn! (Độ tin cậy: ${confidence}%)\n\n`;
      
      // Add warning for low confidence
      if (invoice.confidence < 0.6) {
        message += `⚠️ Lưu ý: Độ tin cậy thấp. Vui lòng kiểm tra lại thông tin.\n\n`;
      }
      
      message += `📋 **Thông tin hóa đơn:**\n`;
      message += `• Loại: ${invoice.invoice_type === 'momo_payment' ? '💳 Thanh toán MoMo' : invoice.invoice_type === 'electricity' ? '⚡ Hóa đơn điện' : '📄 Hóa đơn thông thường'}\n`;
      message += `• Mã số: ${invoice.invoice_code}\n`;
      message += `• Ngày: ${invoice.date}\n`;
      message += `• Người bán: ${invoice.seller_name}\n`;
      message += `• Người mua: ${invoice.buyer_name}\n`;
      
      // Add address if available
      if (invoice.seller_address) {
        message += `• Địa chỉ người bán: ${invoice.seller_address}\n`;
      }
      if (invoice.buyer_address) {
        message += `• Địa chỉ người mua: ${invoice.buyer_address}\n`;
      }
      
      // Add tax info if available
      if (invoice.seller_tax_id) {
        message += `• MST người bán: ${invoice.seller_tax_id}\n`;
      }
      if (invoice.buyer_tax_id) {
        message += `• MST người mua: ${invoice.buyer_tax_id}\n`;
      }
      
      message += `\n💰 **Chi tiết thanh toán:**\n`;
      
      if (invoice.subtotal > 0) {
        message += `• Tổng trước thuế: ${invoice.subtotal.toLocaleString('vi-VN')} ${invoice.currency}\n`;
      }
      if (invoice.tax_amount > 0) {
        message += `• Thuế VAT (${invoice.tax_percentage}%): ${invoice.tax_amount.toLocaleString('vi-VN')} ${invoice.currency}\n`;
      }
      message += `• **Tổng cộng: ${invoice.total_amount}**\n`;
      
      // Add items if available
      let items = invoice.items;
      if (typeof items === 'string') {
        try {
          items = JSON.parse(items);
        } catch (e) {
          console.error('Failed to parse items JSON:', e);
          items = [];
        }
      }
      
      if (items && Array.isArray(items) && items.length > 0) {
        message += `\n📦 **Sản phẩm/Dịch vụ:**\n`;
        items.forEach((item: any, index: number) => {
          message += `${index + 1}. ${item.name || item.description || 'Không rõ'}`;
          if (item.quantity) {
            message += ` - SL: ${item.quantity}`;
          }
          if (item.price) {
            message += ` - ${item.price.toLocaleString('vi-VN')} VNĐ`;
          }
          if (item.amount) {
            message += ` (Tổng: ${item.amount.toLocaleString('vi-VN')} VNĐ)`;
          }
          message += '\n';
        });
      }
      
      // Show OCR text preview if available
      if (data.ocr_text && invoice.confidence < 0.8) {
        message += `\n📝 **Văn bản OCR (đầu tiên):**\n${data.ocr_text.substring(0, 200)}...\n`;
      }
      
      message += `\n💾 Đã lưu vào hệ thống.`;
      
      if (invoice.confidence < 0.7) {
        message += `\n\n💡 **Gợi ý:** Để cải thiện độ chính xác:\n• Chụp ảnh rõ nét hơn\n• Đảm bảo đủ ánh sáng\n• Giữ camera song song với hóa đơn\n• Cài đặt Tesseract OCR cho kết quả tốt hơn`;
      }
      
      addBotMessage(message);
      
      // Clear uploaded file after processing
      setUploadedFile(null);
      
      // Reset file input to allow re-uploading the same file
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      if (cameraActive) {
        handleStopCamera();
      }
      
      // Prompt for next action
      setTimeout(() => {
        addBotMessage('📤 **Tiếp theo:**\n\n• Upload file mới\n• Gõ "**mở camera**" để chụp tiếp\n• Gõ "**xem danh sách**" để xem tất cả hóa đơn');
      }, 1000);
      
    } catch (error) {
      setIsTyping(false);
      addBotMessage('❌ Có lỗi xảy ra khi xử lý hóa đơn. Vui lòng thử lại!');
      console.error('Error processing invoice:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendMessage = async () => {
    if (inputMessage.trim()) {
      const currentTime = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
      const userMsg = inputMessage;
      setMessages([...messages, 
        { id: messages.length + 1, text: userMsg, sender: 'user', time: currentTime }
      ]);
      setInputMessage('');
      setIsTyping(true);
      
      try {
        // Call real chat API using apiService
        const data = await apiService.sendChatMessage(userMsg);
        
        // Check if it's a chat command first
        const isCommand = await handleChatCommand(userMsg);
        
        if (!isCommand) {
          setIsTyping(false);
          const botTime = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
          setMessages(prev => [...prev, 
            { id: prev.length + 1, text: data.response, sender: 'bot', time: botTime }
          ]);
          
          // Show action buttons ONLY if asking about capabilities
          const isCapabilityQuestion = 
            (userMsg.toLowerCase().includes('làm gì') || 
             userMsg.toLowerCase().includes('chức năng') ||
             userMsg.toLowerCase().includes('features') ||
             userMsg.toLowerCase().includes('capabilities')) &&
            (userMsg.toLowerCase().includes('có thể') ||
             userMsg.toLowerCase().includes('bạn') ||
             userMsg.toLowerCase().includes('bot') ||
             userMsg.toLowerCase().includes('chatbot') ||
             userMsg.toLowerCase().includes('hệ thống'));
          
          setShowQuickSuggestions(isCapabilityQuestion);
        } else {
          setIsTyping(false);
        }
        
        scrollToBottom();
      } catch (error) {
        setIsTyping(false);
        const botTime = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
        setMessages(prev => [...prev, 
          { id: prev.length + 1, text: 'Xin lỗi, tôi gặp sự cố khi xử lý tin nhắn. Vui lòng thử lại.', sender: 'bot', time: botTime }
        ]);
        console.error('Chat error:', error);
        setShowQuickSuggestions(false);
        scrollToBottom();
      }
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedFile(e.target.files[0]);
      setCameraActive(false);
      addBotMessage(`📁 **Đã tải file:** ${e.target.files[0].name}\n\n💡 Gõ "**xử lý**" hoặc nhấn nút "Xử lý hóa đơn" để phân tích!`);
    }
  };

  const handleStartCamera = async () => {
    try {
      console.log('🎥 Starting camera...');
      console.log('Current cameraActive state:', cameraActive);
      console.log('videoRef.current exists?', !!videoRef.current);
      
      // First set state to trigger render with video element
      setUploadedFile(null);
      setCameraActive(true);
      console.log('✅ State set to TRUE, triggering re-render...');
      
      // Wait a tick for React to render the video element
      await new Promise(resolve => setTimeout(resolve, 100));
      console.log('After timeout, videoRef.current exists?', !!videoRef.current);
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720 } 
      });
      
      console.log('✅ Stream obtained:', stream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        console.log('✅ Video srcObject set to video element');
        
        // Play the video
        try {
          await videoRef.current.play();
          console.log('✅ Video playing');
        } catch (playErr) {
          console.log('Video play warning (can be ignored):', playErr);
        }
      } else {
        console.error('❌ videoRef.current is still null after state update!');
      }
    } catch (err) {
      console.error('❌ Camera error:', err);
      setCameraActive(false); // Reset state on error
      alert('Không thể truy cập camera. Vui lòng cho phép quyền truy cập.');
    }
  };

  const handleStopCamera = () => {
    console.log('🛑 Stopping camera...');
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => {
        track.stop();
        console.log('Track stopped:', track.kind);
      });
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
    console.log('✅ Camera stopped, cameraActive set to FALSE');
  };

  const handleCapturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      if (context) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], `camera-${Date.now()}.jpg`, { type: 'image/jpeg' });
            setUploadedFile(file);
            handleStopCamera();
          }
        }, 'image/jpeg', 0.95);
      }
    }
  };

  const handleUpdateUser = (name: string, email: string) => {
    if (onUpdateUser) {
      onUpdateUser(name, email);
    }
  };

  // Show Profile Settings
  if (showSettings) {
    return (
      <ProfileSettings 
        user={user} 
        onBack={() => setShowSettings(false)}
        onUpdate={handleUpdateUser}
      />
    );
  }

  // Show Invoice Management Page
  if (currentView === 'invoices') {
    return <InvoiceManagement onBack={() => setCurrentView('dashboard')} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-xl border-b border-gray-200 sticky top-0 z-50">
        <div className="px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Invoice Manager
              </h1>
              <p className="text-xs text-muted-foreground">Dashboard người dùng</p>
            </div>
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-4">
            {/* Notifications */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="relative">
                  <Bell className="h-5 w-5" />
                  <Badge className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center p-0 bg-red-500">
                    3
                  </Badge>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80">
                <DropdownMenuLabel>Thông báo</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <div className="flex flex-col gap-1">
                    <p className="text-sm">Hóa đơn mới đã được tạo</p>
                    <p className="text-xs text-muted-foreground">5 phút trước</p>
                  </div>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <div className="flex flex-col gap-1">
                    <p className="text-sm">Thanh toán thành công</p>
                    <p className="text-xs text-muted-foreground">1 giờ trước</p>
                  </div>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <div className="flex flex-col gap-1">
                    <p className="text-sm">Cập nhật hệ thống</p>
                    <p className="text-xs text-muted-foreground">2 giờ trước</p>
                  </div>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-2">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src="" />
                    <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white">
                      {user.name.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="text-left hidden md:block">
                    <p className="text-sm">{user.name}</p>
                    <p className="text-xs text-muted-foreground">{user.email}</p>
                  </div>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Tài khoản của tôi</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setShowSettings(true)}>
                  <User className="mr-2 h-4 w-4" />
                  <span>Thông tin cá nhân</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onLogout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Đăng xuất</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Camera/Upload Panel */}
          <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-shadow duration-300 flex flex-col h-[700px]">
            <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-purple-50 flex-shrink-0">
              <CardTitle className="flex items-center gap-2">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-md">
                  <Camera className="w-5 h-5 text-white" />
                </div>
                <div>
                  <div>Camera / Upload File</div>
                  <CardDescription className="mt-1">
                    Sử dụng camera hoặc tải lên file hóa đơn
                  </CardDescription>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 p-6 flex-1 flex flex-col overflow-hidden">
              {/* Preview Area */}
              <div className="relative flex-1 bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl overflow-hidden flex items-center justify-center border-2 border-dashed border-gray-300 hover:border-blue-400 transition-all duration-300 group">
                {cameraActive ? (
                  /* Camera Active View */
                  <>
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      className="w-full h-full object-cover"
                    />
                    <canvas ref={canvasRef} className="hidden" />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent pointer-events-none"></div>
                    <Button
                      size="icon"
                      variant="destructive"
                      className="absolute top-4 right-4 shadow-xl hover:scale-110 transition-transform duration-200 z-10 bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 border-2 border-white/50"
                      onClick={handleStopCamera}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                    {/* Capture Button */}
                    <Button
                      size="lg"
                      className="absolute bottom-6 left-1/2 -translate-x-1/2 shadow-2xl hover:scale-110 transition-all duration-200 z-10 bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 border-2 border-white/50 px-8 py-6 rounded-full"
                      onClick={handleCapturePhoto}
                    >
                      <Camera className="w-6 h-6 mr-2" />
                      <span className="text-lg font-semibold">Chụp ảnh</span>
                    </Button>
                    {/* Recording Indicator */}
                    <div className="absolute top-4 left-4 flex items-center gap-2 bg-gradient-to-r from-green-500 to-emerald-600 backdrop-blur-sm px-3 py-2 rounded-full shadow-lg">
                      <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
                      <span className="text-white text-xs">Camera đang bật</span>
                    </div>
                  </>
                ) : uploadedFile ? (
                  <div className="text-center p-8 animate-in fade-in zoom-in duration-300">
                    <div className="relative inline-block">
                      <div className="w-24 h-24 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl animate-pulse">
                        <FileText className="w-12 h-12 text-white" />
                      </div>
                      <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center shadow-lg">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    </div>
                    <p className="mb-2 text-lg">{uploadedFile.name}</p>
                    <p className="text-sm text-muted-foreground mb-1">
                      {(uploadedFile.size / 1024).toFixed(2)} KB
                    </p>
                    <div className="flex items-center justify-center gap-2 text-xs text-green-600 mb-4">
                      <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                      <span>Đã tải lên thành công</span>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      className="mt-4 bg-gradient-to-r from-red-50 to-rose-50 hover:from-red-100 hover:to-rose-100 text-red-600 border-2 border-red-300 hover:border-red-400 hover:shadow-lg transition-all duration-200 hover:scale-105"
                      onClick={() => {
                        setUploadedFile(null);
                        if (fileInputRef.current) {
                          fileInputRef.current.value = '';
                        }
                      }}
                    >
                      <X className="w-4 h-4 mr-2" />
                      Xóa file
                    </Button>
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground p-8">
                    <div className="relative inline-block mb-6">
                      <div className="w-24 h-24 bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform duration-300">
                        <Camera className="w-12 h-12 text-blue-600 opacity-70" />
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-br from-blue-400 via-purple-400 to-pink-400 rounded-full opacity-0 group-hover:opacity-20 animate-pulse transition-opacity duration-300"></div>
                    </div>
                    <p className="text-lg mb-2">Chưa có nội dung</p>
                    <p className="text-sm text-muted-foreground">
                      Kéo thả file vào đây hoặc nhấn nút bên dưới
                    </p>
                    <div className="flex items-center gap-2 justify-center mt-4 text-xs">
                      <span className="px-2 py-1 bg-gradient-to-r from-blue-100 to-blue-200 text-blue-700 rounded-full">JPG</span>
                      <span className="px-2 py-1 bg-gradient-to-r from-purple-100 to-purple-200 text-purple-700 rounded-full">PNG</span>
                      <span className="px-2 py-1 bg-gradient-to-r from-green-100 to-green-200 text-green-700 rounded-full">PDF</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-3">
                <Button
                  className={`h-14 shadow-lg hover:shadow-2xl hover:scale-105 transition-all duration-200 border ${
                    cameraActive 
                      ? 'bg-gradient-to-r from-red-500 via-red-600 to-rose-600 hover:from-red-600 hover:via-red-700 hover:to-rose-700 hover:shadow-red-500/50 border-red-400/30'
                      : 'bg-gradient-to-r from-blue-500 via-blue-600 to-cyan-600 hover:from-blue-600 hover:via-blue-700 hover:to-cyan-700 hover:shadow-blue-500/50 border-blue-400/30'
                  }`}
                  onClick={cameraActive ? handleStopCamera : handleStartCamera}
                >
                  <div className="flex flex-col items-center gap-1">
                    <Camera className="w-5 h-5" />
                    <span className="text-xs">{cameraActive ? 'Đóng Camera' : 'Mở Camera'}</span>
                  </div>
                </Button>
                <Button
                  className="h-14 bg-gradient-to-r from-purple-500 via-purple-600 to-pink-600 hover:from-purple-600 hover:via-purple-700 hover:to-pink-700 shadow-lg hover:shadow-2xl hover:shadow-purple-500/50 hover:scale-105 transition-all duration-200 border border-purple-400/30"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="flex flex-col items-center gap-1">
                    <Upload className="w-5 h-5" />
                    <span className="text-xs">Upload File</span>
                  </div>
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept="image/*,.pdf"
                  onChange={handleFileUpload}
                />
              </div>

              {/* Process Button */}
              <Button 
                className="w-full h-14 bg-gradient-to-r from-emerald-500 via-green-600 to-teal-600 hover:from-emerald-600 hover:via-green-700 hover:to-teal-700 shadow-xl hover:shadow-2xl hover:shadow-green-500/50 hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:scale-100 disabled:cursor-not-allowed text-lg group border border-emerald-400/30"
                disabled={(!cameraActive && !uploadedFile) || isProcessing}
                onClick={handleProcessInvoice}
              >
                <div className="flex items-center gap-2">
                  {isProcessing ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                      <span>Đang xử lý...</span>
                    </>
                  ) : (
                    <>
                      <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center group-hover:rotate-90 transition-transform duration-300 backdrop-blur-sm border border-white/30">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                      <span>Xử lý hóa đơn</span>
                    </>
                  )}
                </div>
              </Button>
            </CardContent>
          </Card>

          {/* Chatbot Panel */}
          <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-shadow duration-300 flex flex-col h-[700px]">
            <CardHeader className="border-b bg-gradient-to-r from-green-50 to-emerald-50 flex-shrink-0">
              <CardTitle className="flex items-center gap-2">
                <div className="relative">
                  <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-md">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  <span className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 border-2 border-white rounded-full animate-pulse"></span>
                </div>
                <div>
                  <div>AI Assistant</div>
                  <CardDescription className="mt-1">
                    Trợ lý thông minh 24/7
                  </CardDescription>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
                    } animate-in fade-in slide-in-from-bottom-3 duration-300`}
                  >
                    <Avatar className={`w-8 h-8 flex-shrink-0 ${
                      message.sender === 'bot' ? 'bg-gradient-to-br from-green-500 to-emerald-500' : 'bg-gradient-to-br from-blue-500 to-purple-500'
                    }`}>
                      <AvatarFallback className="text-white">
                        {message.sender === 'bot' ? 'AI' : user.name.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className={`flex flex-col ${message.sender === 'user' ? 'items-end' : 'items-start'} max-w-[80%]`}>
                      <div
                        className={`px-4 py-3 rounded-2xl ${
                          message.sender === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-tr-sm'
                            : 'bg-gray-100 text-gray-800 rounded-tl-sm'
                        } shadow-sm`}
                      >
                        <p className="text-sm leading-relaxed">{message.text}</p>
                      </div>
                      <span className="text-xs text-muted-foreground mt-1 px-2">
                        {message.time}
                      </span>
                    </div>
                  </div>
                ))}
                
                {/* Typing Indicator */}
                {/* Quick Suggestions */}
                {showQuickSuggestions && (
                  <div className="flex flex-col gap-3 animate-in fade-in slide-in-from-bottom-3 duration-500">
                    <div className="flex gap-3">
                      <Avatar className="w-8 h-8 flex-shrink-0 bg-gradient-to-br from-green-500 to-emerald-500">
                        <AvatarFallback className="text-white">AI</AvatarFallback>
                      </Avatar>
                      <div className="flex flex-col gap-2 flex-1">
                        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm">
                          <p className="text-sm font-semibold text-green-800 mb-1">🎯 Tôi có thể giúp bạn:</p>
                          <p className="text-xs text-green-600">Chọn một hành động bên dưới</p>
                        </div>
                        <div className="grid grid-cols-2 gap-2 ml-11">
                          <Button
                            onClick={() => handleActionButton('📋 Xem danh sách hóa đơn')}
                            variant="outline"
                            className="justify-start text-left h-auto py-3 px-4 hover:bg-blue-50 hover:border-blue-400 hover:text-blue-700 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105"
                          >
                            <FileText className="w-4 h-4 mr-2 flex-shrink-0" />
                            <span className="text-sm font-medium">Xem danh sách</span>
                          </Button>
                          <Button
                            onClick={() => handleActionButton('🔍 Tìm kiếm hóa đơn')}
                            variant="outline"
                            className="justify-start text-left h-auto py-3 px-4 hover:bg-purple-50 hover:border-purple-400 hover:text-purple-700 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105"
                          >
                            <svg className="w-4 h-4 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            <span className="text-sm font-medium">Tìm kiếm</span>
                          </Button>
                          <Button
                            onClick={() => handleActionButton('📅 Lọc theo ngày')}
                            variant="outline"
                            className="justify-start text-left h-auto py-3 px-4 hover:bg-green-50 hover:border-green-400 hover:text-green-700 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105"
                          >
                            <svg className="w-4 h-4 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <span className="text-sm font-medium">Lọc theo ngày</span>
                          </Button>
                          <Button
                            onClick={() => handleActionButton('📊 Xuất báo cáo')}
                            variant="outline"
                            className="justify-start text-left h-auto py-3 px-4 hover:bg-orange-50 hover:border-orange-400 hover:text-orange-700 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105"
                          >
                            <svg className="w-4 h-4 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <span className="text-sm font-medium">Xuất báo cáo</span>
                          </Button>
                          <Button
                            onClick={() => handleActionButton('📈 Thống kê')}
                            variant="outline"
                            className="justify-start text-left h-auto py-3 px-4 hover:bg-pink-50 hover:border-pink-400 hover:text-pink-700 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105"
                          >
                            <svg className="w-4 h-4 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            <span className="text-sm font-medium">Thống kê</span>
                          </Button>
                          <Button
                            onClick={() => handleQuickSuggestion('Hướng dẫn sử dụng hệ thống')}
                            variant="outline"
                            className="justify-start text-left h-auto py-3 px-4 hover:bg-indigo-50 hover:border-indigo-400 hover:text-indigo-700 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-105"
                          >
                            <svg className="w-4 h-4 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span className="text-sm font-medium">Hướng dẫn</span>
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {isTyping && (
                  <div className="flex gap-3 animate-in fade-in slide-in-from-bottom-3 duration-300">
                    <Avatar className="w-8 h-8 flex-shrink-0 bg-gradient-to-br from-green-500 to-emerald-500">
                      <AvatarFallback className="text-white">AI</AvatarFallback>
                    </Avatar>
                    <div className="bg-gray-100 px-5 py-3 rounded-2xl rounded-tl-sm shadow-sm">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t p-4 bg-gray-50 flex-shrink-0">
                <div className="flex gap-2">
                  <Input
                    placeholder="Nhập tin nhắn của bạn..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="flex-1 bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500 transition-all"
                  />
                  <Button
                    onClick={handleSendMessage}
                    className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 shadow-md hover:shadow-lg hover:scale-105 transition-all duration-200"
                    size="icon"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
