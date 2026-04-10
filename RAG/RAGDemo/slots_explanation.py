"""
__slots__ 原理和内存节省机制演示

这个程序详细解释了 __slots__ 的工作原理和为什么能节省内存
"""

import sys
import time
from dataclasses import dataclass
import tracemalloc


# ============================================================
# 第一部分：传统 Python 对象的内存结构
# ============================================================

class TraditionalPerson:
    """传统 Python 类，使用 __dict__ 存储属性"""
    def __init__(self, name, age, email, phone):
        self.name = name
        self.age = age
        self.email = email
        self.phone = phone


def demonstrate_traditional_memory():
    """演示传统对象的内存结构"""
    print("=" * 60)
    print("📊 传统 Python 对象的内存结构")
    print("=" * 60)
    
    person = TraditionalPerson("张三", 30, "zhangsan@example.com", "13800138000")
    
    print(f"对象地址: {hex(id(person))}")
    print(f"对象大小: {sys.getsizeof(person)} bytes")
    print(f"__dict__ 大小: {sys.getsizeof(person.__dict__)} bytes")
    print(f"__dict__ 内容: {person.__dict__}")
    print(f"__dict__ 地址: {hex(id(person.__dict__))}")
    
    print("\n🔍 内存结构分析:")
    print("  1. 对象本身: 包含类型指针和引用计数")
    print("  2. __dict__: 一个字典，存储所有属性")
    print("  3. 每个属性值: 独立的 Python 对象")
    
    # 计算总内存占用
    total_memory = sys.getsizeof(person) + sys.getsizeof(person.__dict__)
    for key, value in person.__dict__.items():
        total_memory += sys.getsizeof(key) + sys.getsizeof(value)
    
    print(f"\n📈 总内存占用: ~{total_memory} bytes")
    print(f"   - 对象本身: {sys.getsizeof(person)} bytes")
    print(f"   - __dict__: {sys.getsizeof(person.__dict__)} bytes")
    print(f"   - 属性值: ~{total_memory - sys.getsizeof(person) - sys.getsizeof(person.__dict__)} bytes")


# ============================================================
# 第二部分：使用 __slots__ 的对象内存结构
# ============================================================

class SlotsPerson:
    """使用 __slots__ 的类"""
    __slots__ = ['name', 'age', 'email', 'phone']
    
    def __init__(self, name, age, email, phone):
        self.name = name
        self.age = age
        self.email = email
        self.phone = phone


def demonstrate_slots_memory():
    """演示 __slots__ 对象的内存结构"""
    print("\n" + "=" * 60)
    print("📊 使用 __slots__ 的对象内存结构")
    print("=" * 60)
    
    person = SlotsPerson("李四", 25, "lisi@example.com", "13900139000")
    
    print(f"对象地址: {hex(id(person))}")
    print(f"对象大小: {sys.getsizeof(person)} bytes")
    print(f"是否有 __dict__: {hasattr(person, '__dict__')}")
    print(f"是否有 __slots__: {hasattr(person, '__slots__')}")
    print(f"__slots__ 内容: {person.__slots__}")
    
    print("\n🔍 内存结构分析:")
    print("  1. 对象本身: 包含类型指针和预分配的属性槽位")
    print("  2. 没有 __dict__: 属性直接存储在对象的固定槽位中")
    print("  3. 每个属性值: 仍然存储为独立的 Python 对象")
    
    # 计算总内存占用
    total_memory = sys.getsizeof(person)
    for attr in person.__slots__:
        value = getattr(person, attr)
        total_memory += sys.getsizeof(value)
    
    print(f"\n📈 总内存占用: ~{total_memory} bytes")
    print(f"   - 对象本身: {sys.getsizeof(person)} bytes")
    print(f"   - 属性值: ~{total_memory - sys.getsizeof(person)} bytes")


# ============================================================
# 第三部分：内存占用对比
# ============================================================

def compare_memory_usage():
    """对比传统对象和 __slots__ 对象的内存占用"""
    print("\n" + "=" * 60)
    print("📊 内存占用对比")
    print("=" * 60)
    
    # 创建大量对象进行对比
    num_objects = 10000
    
    # 传统对象
    tracemalloc.start()
    traditional_people = [TraditionalPerson(f"用户{i}", i % 100, f"user{i}@example.com", f"138{i:08d}") 
                          for i in range(num_objects)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    traditional_memory = peak / 1024 / 1024  # 转换为 MB
    del traditional_people
    
    # __slots__ 对象
    tracemalloc.start()
    slots_people = [SlotsPerson(f"用户{i}", i % 100, f"user{i}@example.com", f"138{i:08d}") 
                    for i in range(num_objects)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    slots_memory = peak / 1024 / 1024  # 转换为 MB
    del slots_people
    
    print(f"📈 创建 {num_objects:,} 个对象的内存占用:")
    print(f"  传统对象: {traditional_memory:.2f} MB")
    print(f"  __slots__ 对象: {slots_memory:.2f} MB")
    print(f"  节省内存: {traditional_memory - slots_memory:.2f} MB")
    print(f"  节省比例: {((traditional_memory - slots_memory) / traditional_memory * 100):.1f}%")


# ============================================================
# 第四部分：属性访问速度对比
# ============================================================

def compare_attribute_access():
    """对比属性访问速度"""
    print("\n" + "=" * 60)
    print("📊 属性访问速度对比")
    print("=" * 60)
    
    num_iterations = 1000000
    
    # 传统对象
    traditional_person = TraditionalPerson("测试", 30, "test@example.com", "13800138000")
    start_time = time.time()
    for _ in range(num_iterations):
        _ = traditional_person.name
        _ = traditional_person.age
        _ = traditional_person.email
        _ = traditional_person.phone
    traditional_time = time.time() - start_time
    
    # __slots__ 对象
    slots_person = SlotsPerson("测试", 30, "test@example.com", "13800138000")
    start_time = time.time()
    for _ in range(num_iterations):
        _ = slots_person.name
        _ = slots_person.age
        _ = slots_person.email
        _ = slots_person.phone
    slots_time = time.time() - start_time
    
    print(f"📈 访问属性 {num_iterations:,} 次的耗时:")
    print(f"  传统对象: {traditional_time:.4f} 秒")
    print(f"  __slots__ 对象: {slots_time:.4f} 秒")
    print(f"  速度提升: {((traditional_time - slots_time) / traditional_time * 100):.1f}%")


# ============================================================
# 第五部分：__slots__ 的底层原理
# ============================================================

def explain_slots_mechanism():
    """解释 __slots__ 的底层工作原理"""
    print("\n" + "=" * 60)
    print("🔬 __slots__ 的底层工作原理")
    print("=" * 60)
    
    print("""
1. 传统对象的内存布局:
   
   ┌─────────────────────────────────────┐
   │ PyObject_HEAD (16 bytes)           │
   │  - 类型指针 (8 bytes)               │
   │  - 引用计数 (8 bytes)               │
   ├─────────────────────────────────────┤
   │ __dict__ 指针 (8 bytes)            │
   └─────────────────────────────────────┘
                    ↓
   ┌─────────────────────────────────────┐
   │ __dict__ (哈希表)                   │
   │  - "name" → "张三"                  │
   │  - "age" → 30                       │
   │  - "email" → "zhangsan@example.com"│
   │  - "phone" → "13800138000"         │
   └─────────────────────────────────────┘

   问题:
   - __dict__ 是一个哈希表，有额外开销
   - 每个对象都需要独立的 __dict__
   - 属性访问需要哈希查找


2. __slots__ 对象的内存布局:
   
   ┌─────────────────────────────────────┐
   │ PyObject_HEAD (16 bytes)           │
   │  - 类型指针 (8 bytes)               │
   │  - 引用计数 (8 bytes)               │
   ├─────────────────────────────────────┤
   │ name 槽位 (8 bytes)                │
   ├─────────────────────────────────────┤
   │ age 槽位 (8 bytes)                 │
   ├─────────────────────────────────────┤
   │ email 槽位 (8 bytes)               │
   ├─────────────────────────────────────┤
   │ phone 槽位 (8 bytes)               │
   └─────────────────────────────────────┘

   优势:
   - 属性直接存储在对象的固定位置
   - 没有 __dict__ 的哈希表开销
   - 属性访问是直接的内存偏移量
   - 编译时就知道属性的位置


3. 为什么节省内存:
   
   a) 消除 __dict__:
      - 传统: 每个对象都有独立的 __dict__ (约 72 bytes)
      - __slots__: 完全消除 __dict__
   
   b) 减少间接引用:
      - 传统: 对象 → __dict__ → 属性值
      - __slots__: 对象 → 属性值
   
   c) 固定大小:
      - 传统: __dict__ 可以动态增长
      - __slots__: 大小固定，预分配


4. 为什么访问更快:
   
   传统访问:
   - 需要在 __dict__ 中哈希查找属性名
   - 时间复杂度: O(1) 但有常数开销
   
   __slots__ 访问:
   - 直接通过内存偏移量访问
   - 类似于 C 结构体的成员访问
   - 时间复杂度: O(1) 且常数开销更小
    """)


# ============================================================
# 第六部分：实际应用示例
# ============================================================

class TraditionalRAG:
    """传统 RAG 类"""
    def __init__(self):
        self._embed_model = None
        self._vector_db = None
        self._llm = None
        self._cache = None
        self._config = None


class SlotsRAG:
    """使用 __slots__ 的 RAG 类"""
    __slots__ = ['_embed_model', '_vector_db', '_llm', '_cache', '_config']
    
    def __init__(self):
        self._embed_model = None
        self._vector_db = None
        self._llm = None
        self._cache = None
        self._config = None


def demonstrate_rag_application():
    """演示在 RAG 应用中的内存节省"""
    print("\n" + "=" * 60)
    print("📊 RAG 应用中的内存节省")
    print("=" * 60)
    
    num_instances = 1000
    
    # 传统 RAG 实例
    tracemalloc.start()
    traditional_rags = [TraditionalRAG() for _ in range(num_instances)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    traditional_memory = peak / 1024 / 1024
    del traditional_rags
    
    # __slots__ RAG 实例
    tracemalloc.start()
    slots_rags = [SlotsRAG() for _ in range(num_instances)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    slots_memory = peak / 1024 / 1024
    del slots_rags
    
    print(f"📈 创建 {num_instances:,} 个 RAG 实例的内存占用:")
    print(f"  传统实现: {traditional_memory:.2f} MB")
    print(f"  __slots__ 实现: {slots_memory:.2f} MB")
    print(f"  节省内存: {traditional_memory - slots_memory:.2f} MB")
    print(f"  节省比例: {((traditional_memory - slots_memory) / traditional_memory * 100):.1f}%")
    
    print("\n💡 在实际应用中:")
    print("  - 如果创建 10,000 个实例，可节省 ~{:.2f} MB 内存".format(
        (traditional_memory - slots_memory) * 10))
    print("  - 如果创建 100,000 个实例，可节省 ~{:.2f} MB 内存".format(
        (traditional_memory - slots_memory) * 100))


# ============================================================
# 第七部分：__slots__ 的限制和注意事项
# ============================================================

def explain_slots_limitations():
    """解释 __slots__ 的限制"""
    print("\n" + "=" * 60)
    print("⚠️  __slots__ 的限制和注意事项")
    print("=" * 60)
    
    print("""
1. 不能动态添加属性:
   
   传统对象:
   >>> person = TraditionalPerson("张三", 30, "zhangsan@example.com", "13800138000")
   >>> person.address = "北京市"  # ✅ 可以动态添加
   
   __slots__ 对象:
   >>> person = SlotsPerson("李四", 25, "lisi@example.com", "13900139000")
   >>> person.address = "北京市"  # ❌ 会抛出 AttributeError


2. 继承时的注意事项:
   
   - 子类会继承父类的 __slots__
   - 如果子类定义自己的 __slots__，父类的 __slots__ 仍然有效
   - 需要在子类的 __slots__ 中包含父类的 __slots__


3. 与 __weakref__ 的冲突:
   
   - 如果需要弱引用，需要在 __slots__ 中包含 '__weakref__'
   
   class WeakRefExample:
       __slots__ = ['name', '__weakref__']


4. 不适用于所有场景:
   
   ✅ 适合:
   - 属性固定的类
   - 需要创建大量实例的类
   - 性能敏感的应用
   
   ❌ 不适合:
   - 需要动态添加属性的类
   - 属性经常变化的类
   - 小规模应用


5. 与 dataclass 的兼容性:
   
   - Python 3.10+ 支持 dataclass 和 __slots__ 结合使用
   
   @dataclass(slots=True)
   class Person:
       name: str
       age: int
    """)


# ============================================================
# 主函数
# ============================================================

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🎯 __slots__ 原理和内存节省机制详解")
    print("=" * 70)
    
    demonstrate_traditional_memory()
    demonstrate_slots_memory()
    compare_memory_usage()
    compare_attribute_access()
    explain_slots_mechanism()
    demonstrate_rag_application()
    explain_slots_limitations()
    
    print("\n" + "=" * 70)
    print("📝 总结")
    print("=" * 70)
    print("""
__slots__ 的核心原理:
1. 消除 __dict__，将属性直接存储在对象的固定槽位中
2. 减少内存开销，通常可节省 40-60% 的内存
3. 提高属性访问速度，通常可提升 10-20%
4. 适用于属性固定、需要大量实例的场景

何时使用 __slots__:
✅ 属性固定的类
✅ 需要创建大量实例
✅ 内存敏感的应用
✅ 性能关键路径

何时不使用 __slots__:
❌ 需要动态添加属性
❌ 属性经常变化
❌ 小规模应用
❌ 开发调试阶段
    """)


if __name__ == "__main__":
    main()