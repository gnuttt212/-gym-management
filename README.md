# GYM Manager – Hệ Thống Quản Lý Phòng Tập Gym

> Đồ án môn học Công nghệ Phần Mềm – Xây dựng hệ thống quản lý phòng tập gym.

## Mô Tả

Hệ thống quản lý phòng tập gym hỗ trợ 5 vai trò người dùng, bao gồm các chức năng:

- **Quản trị viên (ADMIN):** Xem báo cáo thống kê (biểu đồ), quản lý cài đặt hệ thống (giá gói, danh mục bài tập, quy định).
- **Lễ tân (RECEPTIONIST):** Lập danh sách hội viên, đăng ký gói tập tại quầy.
- **Huấn luyện viên (TRAINER):** Lập lịch tập cá nhân cho hội viên.
- **Thu ngân (CASHIER):** Quản lý hóa đơn, xác nhận thanh toán.
- **Hội viên (MEMBER):** Đăng ký trực tuyến, xem lịch tập và hóa đơn cá nhân.

## Tính Năng Chính

| Chức năng | Mô tả |
|-----------|--------|
| Đăng ký hội viên | Trực tuyến hoặc tại quầy, gửi email xác nhận qua SMTP |
| Quản lý gói tập | 4 gói: 1 / 3 / 6 / 12 tháng, giá cấu hình được |
| Lịch tập cá nhân | HLV lập kế hoạch: bài tập, số hiệp, số lần/hiệp, ngày tập trong tuần |
| Thanh toán | Thu ngân xác nhận thủ công (tiền mặt / chuyển khoản) |
| Báo cáo & thống kê | Biểu đồ Chart.js: hội viên theo tháng, doanh thu, hội viên đang hoạt động |
| Phân quyền | 5 vai trò, kiểm tra quyền ở cả route và service |
| Email bất đồng bộ | Gửi qua hàng đợi Redis, có retry và ghi log |

## Kiến Trúc

```
Modular Monolith

Route (Blueprint) → Service (Business Logic) → Repository (Data Access) → Model (ORM)
```

**Nguyên tắc:**
- Route chỉ nhận request và render template, không chứa logic nghiệp vụ.
- Service chứa toàn bộ nghiệp vụ, phụ thuộc abstraction (interface).
- Repository chỉ truy vấn database.
- Phân quyền bằng decorator `@roles_required(...)`.

## 🛠️ Công Nghệ

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Python 3.11, Flask, SQLAlchemy, Flask-Migrate |
| Database | MySQL 8 |
| Session & Queue | Redis |
| Frontend | HTML, CSS, JavaScript, Bootstrap 5, Chart.js |
| Validation | marshmallow, Flask-WTF (CSRF) |
| Email | Flask-Mail (SMTP) |
| Triển khai | Docker Compose |

## Cấu Trúc Thư Mục

```
gym-management/
├── docker-compose.yml          # 3 services: web, mysql, redis
├── Dockerfile                  # Python 3.11-slim
├── .env.example                # Template biến môi trường
├── requirements.txt            # Dependencies
├── run.py                      # Entry point
├── app/
│   ├── __init__.py             # App factory
│   ├── config.py               # Cấu hình (Dev/Prod/Testing)
│   ├── extensions.py           # SQLAlchemy, Mail, Redis, CSRF
│   ├── errors.py               # Error handlers
│   ├── models/                 # ORM models (11 bảng)
│   ├── auth/                   # Xác thực & phân quyền
│   ├── members/                # Quản lý hội viên
│   ├── subscriptions/          # Gói tập & đăng ký
│   ├── training/               # Bài tập & lịch tập
│   ├── billing/                # Hóa đơn & thanh toán
│   ├── reports/                # Báo cáo & thống kê
│   ├── settings/               # Cài đặt hệ thống
│   ├── notifications/          # Gửi email (SMTP)
│   ├── templates/              # Jinja2 templates
│   └── static/                 # CSS, JS
├── seeds/                      # Dữ liệu seed
├── migrations/                 # Flask-Migrate
└── tests/                      # Unit tests
```

## Mô Hình Dữ Liệu

```
users ──────────┐
                ├── members ──── subscriptions ──── invoices
trainers ───────┘       │
                        └── workout_plans ──── workout_plan_items ──── exercises

membership_plans        settings        email_logs
```

**Các bảng chính:**

| Bảng | Mô tả |
|------|--------|
| `users` | Tài khoản đăng nhập (username = SĐT cho MEMBER) |
| `members` | Thông tin hội viên (họ tên, SĐT, giới tính, năm sinh) |
| `trainers` | Huấn luyện viên |
| `membership_plans` | Gói tập (1/3/6/12 tháng + giá) |
| `subscriptions` | Đăng ký gói (ngày bắt đầu, ngày hết hạn) |
| `invoices` | Hóa đơn (price_snapshot, status, paid_at) |
| `exercises` | Danh mục bài tập (xóa mềm) |
| `workout_plans` | Kế hoạch tập luyện |
| `workout_plan_items` | Chi tiết bài tập trong kế hoạch |
| `settings` | Cấu hình hệ thống (key-value) |
| `email_logs` | Log gửi email (PENDING/SENT/FAILED) |

## 🚀 Cài Đặt & Chạy

### Yêu cầu
- [Docker](https://www.docker.com/) & Docker Compose

### Bước 1: Clone repository

```bash
git clone https://github.com/gnuttt212/-gym-management.git
cd gym-management
```

### Bước 2: Tạo file .env

```bash
cp .env.example .env
# Chỉnh sửa .env với thông tin cấu hình của bạn
```

### Bước 3: Chạy Docker Compose

```bash
docker-compose up --build
```

### Bước 4: Truy cập

Mở trình duyệt: [http://localhost:5000](http://localhost:5000)

### Chạy không cần Docker (development)

```bash
# Cài dependencies
pip install -r requirements.txt

# Cần có MySQL và Redis đang chạy
# Cập nhật .env: MYSQL_HOST=localhost, REDIS_HOST=localhost

# Chạy migration
flask db upgrade

# Chạy seed data
python -m seeds.seed

# Khởi động server
python run.py
```

## Quy Tắc Nghiệp Vụ

| Mã | Quy tắc |
|----|---------|
| BR1 | Ngày hết hạn = ngày đăng ký + thời hạn gói. Hội viên "đang hoạt động" khi ngày hiện tại ≤ ngày hết hạn |
| BR2 | Hóa đơn lưu giá tại thời điểm lập (`price_snapshot`). Đổi giá gói không ảnh hưởng hóa đơn cũ |
| BR3 | Số ngày tập trong kế hoạch ≤ `max_days_per_week` (đọc từ bảng settings) |
| BR4 | Mỗi hội viên có tối đa 1 HLV cá nhân |
| BR5 | Gửi email thất bại không hủy đăng ký. Gửi bất đồng bộ, ghi log để retry |
