from typing import Any, Text, Dict, List
import requests
import json
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Backend API configuration
BACKEND_API_URL = "http://localhost:5000/api"

class ActionCreateTemplate(Action):
    def name(self) -> Text:
        return "action_create_template"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        template_name = tracker.get_slot("template_name")
        company_name = tracker.get_slot("company_name")
        
        try:
            # Call backend API to create template
            response = requests.post(f"{BACKEND_API_URL}/templates", json={
                "name": template_name or f"Mẫu hóa đơn {company_name}" if company_name else "Mẫu hóa đơn mới",
                "description": f"Mẫu hóa đơn được tạo cho {company_name}" if company_name else "Mẫu hóa đơn được tạo qua chatbot",
                "field_mappings": {
                    "company_name": "[TÊN CÔNG TY]",
                    "company_address": "[ĐỊA CHỈ]",
                    "invoice_number": "[SỐ HÓA ĐƠN]",
                    "invoice_date": "[NGÀY LẬP]",
                    "customer_name": "[TÊN KHÁCH HÀNG]",
                    "total_amount": "[TỔNG TIỀN]"
                },
                "is_default": False
            })
            
            if response.status_code == 201:
                template = response.json()
                dispatcher.utter_message(text=f"✅ Đã tạo thành công mẫu hóa đơn '{template['name']}'. Mẫu này đã được lưu vào database và có thể sử dụng cho OCR.")
            else:
                dispatcher.utter_message(text="❌ Có lỗi khi tạo mẫu hóa đơn. Vui lòng thử lại sau.")
                
        except Exception as e:
            dispatcher.utter_message(text="❌ Không thể kết nối đến hệ thống backend. Vui lòng kiểm tra kết nối.")
            print(f"Error creating template: {e}")
        
        return []

class ActionProcessOCR(Action):
    def name(self) -> Text:
        return "action_process_ocr"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="📷 Để sử dụng OCR, bạn có thể:\n1. Sử dụng camera để chụp ảnh hóa đơn\n2. Tải lên file ảnh từ máy tính\n3. Chọn mẫu hóa đơn phù hợp để tăng độ chính xác\n\nHãy truy cập giao diện chính để upload ảnh!")
        
        return []

class ActionSearchInvoice(Action):
    def name(self) -> Text:
        return "action_search_invoice"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        invoice_number = tracker.get_slot("invoice_number")
        company_name = tracker.get_slot("company_name")
        customer_name = tracker.get_slot("customer_name")
        
        search_params = {}
        if invoice_number:
            search_params["invoice_number"] = invoice_number
        if company_name:
            search_params["company_name"] = company_name
        if customer_name:
            search_params["customer_name"] = customer_name
            
        try:
            # Call backend API to search invoices
            response = requests.get(f"{BACKEND_API_URL}/invoices/search", params=search_params)
            
            if response.status_code == 200:
                invoices = response.json()
                if invoices:
                    message = f"🔍 Tìm thấy {len(invoices)} hóa đơn:\n"
                    for invoice in invoices[:5]:  # Show max 5 results
                        message += f"• {invoice.get('invoice_number', 'N/A')} - {invoice.get('company_name', 'N/A')} - {invoice.get('total_amount', 'N/A')}\n"
                    dispatcher.utter_message(text=message)
                else:
                    dispatcher.utter_message(text="🔍 Không tìm thấy hóa đơn nào phù hợp với tiêu chí tìm kiếm.")
            else:
                dispatcher.utter_message(text="❌ Có lỗi khi tìm kiếm hóa đơn. Vui lòng thử lại.")
                
        except Exception as e:
            dispatcher.utter_message(text="❌ Không thể kết nối đến hệ thống tìm kiếm.")
            print(f"Error searching invoices: {e}")
        
        return []

class ActionListTemplates(Action):
    def name(self) -> Text:
        return "action_list_templates"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Call backend API to get templates
            response = requests.get(f"{BACKEND_API_URL}/templates")
            
            if response.status_code == 200:
                templates = response.json()
                if templates:
                    message = f"📋 Danh sách mẫu hóa đơn có sẵn ({len(templates)} mẫu):\n"
                    for template in templates:
                        message += f"• {template['name']} - {template['description']}\n"
                    dispatcher.utter_message(text=message)
                else:
                    dispatcher.utter_message(text="📋 Chưa có mẫu hóa đơn nào trong hệ thống. Bạn có thể tạo mẫu mới!")
            else:
                dispatcher.utter_message(text="❌ Có lỗi khi lấy danh sách mẫu.")
                
        except Exception as e:
            dispatcher.utter_message(text="❌ Không thể kết nối đến hệ thống.")
            print(f"Error listing templates: {e}")
        
        return []

class ActionHandleUpload(Action):
    def name(self) -> Text:
        return "action_handle_upload"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        file_type = tracker.get_slot("file_type")
        
        dispatcher.utter_message(text="📤 Để tải lên file hóa đơn:\n1. Sử dụng nút 'Chụp ảnh' để mở camera\n2. Hoặc kéo thả file ảnh vào khung upload\n3. Hỗ trợ các định dạng: JPG, PNG, PDF\n4. Chất lượng ảnh tốt sẽ cho kết quả OCR chính xác hơn\n\nSau khi upload, hệ thống sẽ tự động phân tích và trích xuất thông tin!")
        
        return []

class ActionTrainRasa(Action):
    def name(self) -> Text:
        return "action_train_rasa"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # Call backend API to trigger Rasa training
            response = requests.post(f"{BACKEND_API_URL}/templates/rasa/train")
            
            if response.status_code == 200:
                result = response.json()
                dispatcher.utter_message(text="🤖 Đã bắt đầu quá trình huấn luyện Rasa với dữ liệu mới. Quá trình này có thể mất vài phút.")
            else:
                dispatcher.utter_message(text="❌ Có lỗi khi khởi động quá trình huấn luyện.")
                
        except Exception as e:
            dispatcher.utter_message(text="❌ Không thể kết nối đến hệ thống huấn luyện.")
            print(f"Error training Rasa: {e}")
        
        return []