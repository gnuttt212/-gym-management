# Use Case Diagram - Hệ thống quản lý Gym

## Đăng ký hội viên

```mermaid
usecase-beta
direction LR

actor Member("Hội viên")
actor Receptionist("Lễ tân")

systemBoundary Gym["Hệ thống quản lý Gym"]
    Register("Đăng ký hội viên")
    SelectPackage("Chọn gói tập")
    Payment("Thanh toán")
end

Member --> Register
Receptionist --> Register

Register ..> : include SelectPackage
Register ..> : include Payment
```
