# C++ 核心知识整理：智能指针、移动语义与 RAII

## 目录
1. [RAII (资源获取即初始化)](#1-raii)
2. [移动语义](#2-移动语义)
3. [智能指针](#3-智能指针)
4. [最佳实践与常见陷阱](#4-最佳实践与常见陷阱)

---

## 1. RAII

### 1.1 核心概念
**RAII (Resource Acquisition Is Initialization)** 是 C++ 最重要的编程惯用法：
- **资源获取**：在对象构造时完成
- **资源释放**：在对象析构时自动完成
- **生命周期绑定**：资源生命周期与对象生命周期一致

### 1.2 为什么需要 RAII？
```cpp
// ❌ 传统方式 - 容易出错
void badExample() {
    int* ptr = new int(42);
    // 如果这里抛出异常...
    doSomething();  // 可能抛出异常
    delete ptr;     // 永远不会执行！内存泄漏
}

// ✅ RAII 方式 - 异常安全
void goodExample() {
    std::unique_ptr<int> ptr = std::make_unique<int>(42);
    doSomething();  // 即使抛出异常，ptr 也会自动释放
}  // 自动调用 ~unique_ptr()
```

### 1.3 RAII 实现模板
```cpp
template<typename T>
class RAIIWrapper {
public:
    // 构造时获取资源
    explicit RAIIWrapper(T* resource) : resource_(resource) {}

    // 析构时释放资源
    ~RAIIWrapper() {
        if (resource_) {
            delete resource_;
        }
    }

    // 禁止拷贝（避免重复释放）
    RAIIWrapper(const RAIIWrapper&) = delete;
    RAIIWrapper& operator=(const RAIIWrapper&) = delete;

    // 允许移动
    RAIIWrapper(RAIIWrapper&& other) noexcept : resource_(other.resource_) {
        other.resource_ = nullptr;
    }

    // 访问资源
    T* get() const { return resource_; }
    T& operator*() const { return *resource_; }
    T* operator->() const { return resource_; }

private:
    T* resource_;
};
```

### 1.4 常见 RAII 应用
| 场景 | 标准库类 | 资源类型 |
|------|----------|----------|
| 动态内存 | `std::unique_ptr`, `std::shared_ptr` | 堆内存 |
| 文件操作 | `std::fstream`, `std::ifstream` | 文件句柄 |
| 互斥锁 | `std::lock_guard`, `std::unique_lock` | 互斥量 |
| 动态数组 | `std::vector`, `std::string` | 连续内存 |

---

## 2. 移动语义

### 2.1 左值与右值
```cpp
int x = 42;           // x 是左值，42 是右值
int y = x + 1;        // y 是左值，x+1 是右值
int&& r1 = 42;        // 右值引用绑定到字面量
int&& r2 = x + y;     // 右值引用绑定到临时对象
// int&& r3 = x;      // 错误！右值引用不能绑定到左值

const int& cr = 42;   // const 左值引用可以绑定右值
```

**判断口诀**：
- **左值**：有名字、有地址、可取地址的表达式
- **右值**：临时对象、字面量、将亡值

### 2.2 左值引用 vs 右值引用
```cpp
void process(int& x) {
    std::cout << "左值引用版本: " << x << std::endl;
}

void process(int&& x) {
    std::cout << "右值引用版本: " << x << std::endl;
}

int main() {
    int a = 10;
    process(a);          // 调用左值引用版本
    process(20);         // 调用右值引用版本
    process(std::move(a)); // 调用右值引用版本
}
```

### 2.3 移动构造与移动赋值
```cpp
class MyString {
public:
    // 默认构造
    MyString() : data_(nullptr), size_(0) {}

    // 普通构造
    MyString(const char* str) {
        size_ = strlen(str);
        data_ = new char[size_ + 1];
        strcpy(data_, str);
    }

    // 析构
    ~MyString() { delete[] data_; }

    // 拷贝构造 - 深拷贝
    MyString(const MyString& other) : size_(other.size_) {
        data_ = new char[size_ + 1];
        strcpy(data_, other.data_);
        std::cout << "拷贝构造\n";
    }

    // 移动构造 - 资源转移
    MyString(MyString&& other) noexcept
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;  // 源对象置空
        other.size_ = 0;
        std::cout << "移动构造\n";
    }

    // 拷贝赋值
    MyString& operator=(const MyString& other) {
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = new char[size_ + 1];
            strcpy(data_, other.data_);
        }
        std::cout << "拷贝赋值\n";
        return *this;
    }

    // 移动赋值
    MyString& operator=(MyString&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        std::cout << "移动赋值\n";
        return *this;
    }

private:
    char* data_;
    size_t size_;
};
```

### 2.4 std::move 与 std::forward

```cpp
// std::move - 将左值转换为右值
std::vector<int> v1 = {1, 2, 3};
std::vector<int> v2 = std::move(v1);  // v1 被掏空，v2 接管资源
// 此时 v1 处于有效但未定义的状态

// std::forward - 完美转发
template<typename T>
void wrapper(T&& arg) {
    // 保持原有值类别
    process(std::forward<T>(arg));
}

int main() {
    int x = 10;
    wrapper(x);          // T=int&, 转发为左值
    wrapper(20);         // T=int, 转发为右值
}
```

### 2.5 移动语义规则总结

```
┌─────────────────────────────────────────────────────────────┐
│                    移动语义规则速查表                         │
├─────────────────────────────────────────────────────────────┤
│ T&& + 右值 → 移动语义                                        │
│ const T& + 右值 → 拷贝语义（无法修改）                        │
│ T& + 右值 → 编译错误                                         │
│ std::move(左值) → 右值引用                                   │
│ std::forward<T>(arg) → 保持原有值类别                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 智能指针

### 3.1 智能指针概览
```
┌──────────────────────────────────────────────────────────────────┐
│                        智能指针对比                               │
├──────────────┬─────────────┬─────────────┬──────────────────────┤
│    特性       │ unique_ptr  │ shared_ptr  │     weak_ptr         │
├──────────────┼─────────────┼─────────────┼──────────────────────┤
│ 独占所有权    │     ✅      │     ❌      │        ❌            │
│ 共享所有权    │     ❌      │     ✅      │        ❌            │
│ 引用计数      │     ❌      │     ✅      │   ✅ (不增加计数)     │
│ 可拷贝       │     ❌      │     ✅      │        ✅            │
│ 可移动       │     ✅      │     ✅      │        ✅            │
│ 解决循环引用  │     ❌      │     ❌      │        ✅            │
└──────────────┴─────────────┴─────────────┴──────────────────────┘
```

### 3.2 std::unique_ptr - 独占所有权

```cpp
#include <memory>

// 创建方式
std::unique_ptr<int> p1 = std::make_unique<int>(42);  // 推荐
std::unique_ptr<int> p2(new int(42));                  // 不推荐

// 禁止拷贝
// auto p3 = p1;  // 编译错误！

// 允许移动
auto p3 = std::move(p1);  // p1 变为 nullptr

// 检查和访问
if (p3) {
    std::cout << *p3 << std::endl;      // 解引用
    std::cout << p3.get() << std::endl;  // 获取裸指针
}

// 释放所有权
int* raw = p3.release();  // p3 变为 nullptr，调用者负责删除
delete raw;

// 重置
p3.reset();              // 释放资源，变为 nullptr
p3.reset(new int(100));  // 释放旧资源，接管新资源

// 自定义删除器
auto fileDeleter = [](FILE* f) { fclose(f); };
std::unique_ptr<FILE, decltype(fileDeleter)> file(
    fopen("test.txt", "r"), fileDeleter
);
```

### 3.3 std::shared_ptr - 共享所有权

```cpp
#include <memory>

// 创建方式
auto sp1 = std::make_shared<int>(42);  // 推荐：一次分配
std::shared_ptr<int> sp2(new int(42));  // 两次分配

// 允许拷贝
auto sp3 = sp1;  // 引用计数 +1
auto sp4 = sp1;  // 引用计数 +1

std::cout << sp1.use_count() << std::endl;  // 输出: 3

// 线程安全的引用计数
// 注意：引用计数线程安全，但对象访问需要同步

// 自定义删除器
auto sp = std::shared_ptr<int>(
    new int(42),
    [](int* p) {
        std::cout << "Deleting...\n";
        delete p;
    }
);
```

### 3.4 std::weak_ptr - 打破循环引用

```cpp
#include <memory>

class Node {
public:
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> prev;  // 使用 weak_ptr 打破循环

    ~Node() { std::cout << "Node destroyed\n"; }
};

int main() {
    auto node1 = std::make_shared<Node>();
    auto node2 = std::make_shared<Node>();

    node1->next = node2;
    node2->prev = node1;  // weak_ptr 不增加引用计数

    // 使用 weak_ptr
    if (auto locked = node2->prev.lock()) {
        // locked 是 shared_ptr，可以安全使用
        std::cout << "Prev node exists\n";
    }

    // 检查是否过期
    if (!node2->prev.expired()) {
        std::cout << "Prev node still alive\n";
    }
}
```

### 3.5 循环引用问题与解决

```cpp
// ❌ 循环引用 - 内存泄漏
class BadNode {
public:
    std::shared_ptr<BadNode> next;
    std::shared_ptr<BadNode> prev;  // 强引用导致循环
};

void badExample() {
    auto n1 = std::make_shared<BadNode>();
    auto n2 = std::make_shared<BadNode>();
    n1->next = n2;
    n2->prev = n1;  // 循环形成！
}  // n1, n2 永远不会被释放

// ✅ 使用 weak_ptr 打破循环
class GoodNode {
public:
    std::shared_ptr<GoodNode> next;
    std::weak_ptr<GoodNode> prev;  // 弱引用打破循环
};
```

### 3.6 智能指针与数组

```cpp
// unique_ptr 支持数组
std::unique_ptr<int[]> arr1 = std::make_unique<int[]>(10);
arr1[0] = 42;  // 支持 [] 操作

// shared_ptr 不直接支持数组
// C++17 前：需要自定义删除器
std::shared_ptr<int> arr2(new int[10], std::default_delete<int[]>());

// C++20+：可以使用 make_shared
// 但仍不直接支持 [] 操作
```

---

## 4. 最佳实践与常见陷阱

### 4.1 最佳实践

```cpp
// ✅ 1. 优先使用 make_unique/make_shared
auto p1 = std::make_unique<int>(42);
auto p2 = std::make_shared<int>(42);

// ✅ 2. 使用 auto 减少代码冗余
auto ptr = std::make_unique<MyClass>();

// ✅ 3. 按值返回 unique_ptr
std::unique_ptr<MyClass> create() {
    return std::make_unique<MyClass>();  // RVO 或移动语义
}

// ✅ 4. 函数参数传递
void process(const std::shared_ptr<MyClass>& ptr);  // 共享所有权
void observe(const MyClass& obj);                    // 仅观察
void take(std::unique_ptr<MyClass> ptr);             // 转移所有权

// ✅ 5. 启用移动语义
class MyClass {
public:
    MyClass(MyClass&&) noexcept = default;
    MyClass& operator=(MyClass&&) noexcept = default;
};

// ✅ 6. Rule of Zero - 让编译器生成默认操作
class ModernClass {
    std::string name;
    std::vector<int> data;
    std::unique_ptr<int> ptr;
    // 无需定义任何特殊成员函数！
};
```

### 4.2 常见陷阱

```cpp
// ❌ 陷阱 1：同一裸指针创建多个智能指针
int* raw = new int(42);
std::unique_ptr<int> p1(raw);
std::unique_ptr<int> p2(raw);  // 双重删除！

// ❌ 陷阱 2：this 指针误用
class Bad {
public:
    std::shared_ptr<Bad> getShared() {
        return std::shared_ptr<Bad>(this);  // 错误！
    }
};

// ✅ 正确做法：继承 enable_shared_from_this
class Good : public std::enable_shared_from_this<Good> {
public:
    std::shared_ptr<Good> getShared() {
        return shared_from_this();  // 正确
    }
};

// ❌ 陷阱 3：循环引用（见 3.5 节）

// ❌ 陷阱 4：使用过期 weak_ptr
std::weak_ptr<int> weak;
{
    auto shared = std::make_shared<int>(42);
    weak = shared;
}  // shared 被销毁
// auto bad = *weak.lock();  // 危险！先检查 expired()

// ✅ 安全使用
if (auto shared = weak.lock()) {
    *shared = 100;  // 安全
}

// ❌ 陷阱 5：移动后使用
auto p1 = std::make_unique<int>(42);
auto p2 = std::move(p1);
// std::cout << *p1;  // 未定义行为！p1 为 nullptr
```

### 4.3 智能指针选择指南

```
┌─────────────────────────────────────────────────────────────┐
│                    智能指针选择决策树                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  需要共享所有权吗？                                          │
│       │                                                     │
│       ├── 否 ──→ unique_ptr (首选)                          │
│       │                                                     │
│       └── 是 ──→ 需要观察/打破循环吗？                       │
│                      │                                      │
│                      ├── 否 ──→ shared_ptr                  │
│                      │                                      │
│                      └── 是 ──→ weak_ptr (配合 shared_ptr)  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 性能考虑

```cpp
// shared_ptr 性能开销
// - 控制块内存分配
// - 原子引用计数操作
// - 更大的内存占用

// unique_ptr 性能
// - 零开销抽象（与裸指针相同）
// - 编译时确定删除器

// 优化建议
// 1. 热点路径优先使用 unique_ptr
// 2. 避免频繁的 shared_ptr 拷贝
// 3. 使用 make_* 减少内存分配次数
// 4. 考虑使用对象池管理频繁创建销毁的对象
```

---

## 快速参考卡片

### 智能指针 API 速查
```cpp
// unique_ptr
p.get()          // 获取裸指针
p.release()      // 释放所有权
p.reset()        // 重置为空
p.reset(new T()) // 重置为新对象

// shared_ptr
p.use_count()    // 引用计数
p.unique()       // 是否唯一 (C++17 废弃)
p.get(), p.reset() // 同上

// weak_ptr
p.expired()      // 是否过期
p.lock()         // 获取 shared_ptr
p.use_count()    // 关联的引用计数
```

### 移动语义速查
```cpp
std::move(obj)           // 转换为右值
std::forward<T>(arg)     // 完美转发
T&&                      // 右值引用
noexcept                 // 移动操作应标记
```

---

## 参考资源
- **书籍**：《Effective Modern C++》 - Scott Meyers
- **书籍**：《C++ Primer》 第 5 版
- **在线**：cppreference.com
- **指南**：C++ Core Guidelines (github.com/isocpp/CppCoreGuidelines)
