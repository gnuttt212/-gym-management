# Use Case Diagram — Hệ thống quản lý phòng Gym

Các Use Case được tổ chức theo **6 module chức năng**, thay vì chia theo từng kênh trực tuyến/tại quầy. Mỗi module có một sơ đồ độc lập để dễ đọc và bảo trì.

> Cú pháp: Mermaid `usecase-beta` (cần trình render hỗ trợ Mermaid 12.0.0+).

## Danh sách module

| Module | Chức năng chính |
|---|---|
| Quản lý hội viên | Đăng ký hội viên trực tuyến / tại quầy |
| Quản lý gói tập | Đăng ký và gia hạn gói tập |
| Quản lý thanh toán | Thanh toán, hóa đơn, lịch sử giao dịch |
| Quản lý tập luyện | Phân công HLV, kế hoạch và lịch tập |
| Quản trị hệ thống | Nhân viên, danh mục bài tập, giá và giới hạn ngày tập |
| Báo cáo và thống kê | Hội viên còn hạn, đăng ký, doanh thu |

## 1. Quản lý hội viên

Khách tự đăng ký trực tuyến; lễ tân hỗ trợ đăng ký tại quầy. Cả hai hình thức đều gửi email xác nhận.


```mermaid
usecase-beta
direction LR
actor Guest("Khách")
actor Receptionist("Lễ tân")
actor SMTP("SMTP Server")
systemBoundary MemberModule["Module quản lý hội viên"]@{ type: package }
  RegisterOnline("Đăng ký hội viên trực tuyến")
  RegisterDesk("Đăng ký hội viên tại quầy")
  Register("Đăng ký hội viên")
  SendEmail("Gửi email xác nhận")
end
Guest -- RegisterOnline
Receptionist -- RegisterDesk
SMTP -- SendEmail
RegisterOnline --|> Register
RegisterDesk --|> Register
Register ..> : include SendEmail
```

## 2. Quản lý gói tập

Hội viên đăng ký hoặc gia hạn trực tuyến; lễ tân thực hiện tại quầy. Mỗi hình thức bao gồm thanh toán tương ứng.


```mermaid
usecase-beta
direction LR
actor Member("Hội viên")
actor Receptionist("Lễ tân")
systemBoundary PackageModule["Module quản lý gói tập"]@{ type: package }
  BuyOnline("Đăng ký gói tập trực tuyến")
  RenewOnline("Gia hạn gói tập trực tuyến")
  BuyDesk("Đăng ký gói tập tại quầy")
  RenewDesk("Gia hạn gói tập tại quầy")
end
PayOnline("Thanh toán trực tuyến")
PayDesk("Thanh toán tại quầy")
Member -- BuyOnline
Member -- RenewOnline
Receptionist -- BuyDesk
Receptionist -- RenewDesk
BuyOnline ..> : include PayOnline
RenewOnline ..> : include PayOnline
BuyDesk ..> : include PayDesk
RenewDesk ..> : include PayDesk
```

## 3. Quản lý thanh toán

Thanh toán trực tuyến qua MoMo hoặc tại quầy qua thu ngân; thu ngân lập hóa đơn. Quyền xem lịch sử thanh toán phụ thuộc vai trò.


```mermaid
usecase-beta
direction LR
actor Member("Hội viên")
actor Cashier("Thu ngân")
actor Momo("MoMo")
systemBoundary PaymentModule["Module quản lý thanh toán"]@{ type: package }
  PayOnline("Thanh toán trực tuyến")
  PayDesk("Thanh toán tại quầy")
  Invoice("Lập hóa đơn")
  OwnHistory("Xem lịch sử thanh toán của bản thân")
  MemberHistory("Xem lịch sử thanh toán của hội viên")
end
Member -- OwnHistory
Cashier -- PayDesk
Cashier -- Invoice
Cashier -- MemberHistory
Momo -- PayOnline
PayDesk ..> : include Invoice
```

## 4. Quản lý tập luyện

Lễ tân gán huấn luyện viên; huấn luyện viên xem hội viên phụ trách và lập kế hoạch; hội viên xem lịch tập.


```mermaid
usecase-beta
direction LR
actor Member("Hội viên")
actor Receptionist("Lễ tân")
actor Trainer("Huấn luyện viên")
systemBoundary TrainingModule["Module quản lý tập luyện"]@{ type: package }
  AssignTrainer("Gán HLV cho hội viên")
  AssignedMembers("Xem hội viên phụ trách")
  CreatePlan("Lập kế hoạch tập luyện")
  ViewSchedule("Xem lịch tập")
end
Receptionist -- AssignTrainer
Trainer -- AssignedMembers
Trainer -- CreatePlan
Member -- ViewSchedule
```

## 5. Quản trị hệ thống

Quản trị viên tạo tài khoản nhân viên, quản lý bài tập, giá gói tập và giới hạn ngày tập.


```mermaid
usecase-beta
direction LR
actor Admin("Quản trị viên")
actor SMTP("SMTP Server")
systemBoundary AdminModule["Module quản trị hệ thống"]@{ type: package }
  CreateStaff("Tạo tài khoản nhân viên")
  ManageExercise("Quản lý danh mục bài tập")
  ManagePrice("Quản lý giá gói tập")
  LimitDays("Giới hạn ngày tập")
  SendEmail("Gửi email xác nhận")
end
Admin -- CreateStaff
Admin -- ManageExercise
Admin -- ManagePrice
Admin -- LimitDays
SMTP -- SendEmail
CreateStaff ..> : include SendEmail
```

## 6. Báo cáo và thống kê

Quản trị viên theo dõi hội viên còn hạn, lượng hội viên đăng ký và doanh thu.


```mermaid
usecase-beta
direction LR
actor Admin("Quản trị viên")
systemBoundary ReportModule["Module báo cáo và thống kê"]@{ type: package }
  ViewReports("Xem báo cáo thống kê")
  ActiveMembers("Thống kê hội viên còn hạn")
  NewMembers("Thống kê hội viên đăng ký")
  Revenue("Thống kê doanh thu")
end
Admin -- ViewReports
ActiveMembers --|> ViewReports
NewMembers --|> ViewReports
Revenue --|> ViewReports
```

## Ký hiệu

- `--`: Actor tương tác với Use Case.
- `..> : include`: Use Case này luôn bao gồm hành vi của Use Case được trỏ tới.
- `--|>`: Generalization, mũi tên hướng về Use Case tổng quát.

**Lưu ý:** Trong module **Quản lý gói tập**, hai Use Case thanh toán được đặt ngoài ranh giới module để thể hiện chức năng được sử dụng từ **Module quản lý thanh toán**. Các Use Case dùng chung như **Gửi email xác nhận** được lặp lại để sơ đồ của mỗi module có thể xem độc lập; đó không phải là các chức năng khác nhau.
