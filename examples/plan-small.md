# 小型 Web 项目：日志接入整理

项目是一个内部用的订单管理页面，前端用 Vite + React，后端是 Node.js + Express。最近把日志库从旧的 `oldLogger` 换成了 `newLogger`，但仓库里还有不少地方没跟上。这次计划把剩余的接入工作做完。

1. 找出 `src/` 和 `server/` 下所有调用 `oldLogger` 的位置，按文件分组列出来，标出每个调用点传了哪些参数，特别是带自定义 formatter 的。
2. 按上一步的清单，把 `utils/` 下的 `oldLogger` 调用全部替换成 `newLogger`，保持日志级别和输出字段不变；带 formatter 的地方按新接口改写。
3. 给新日志适配层补单元测试，覆盖默认格式、自定义 formatter 和错误对象序列化三种情况，测试用 `npm test` 跑。
4. 排查设置页偶尔白屏的问题。复现步骤不明，只在刷新几次后出现，控制台有时报 `Cannot read properties of undefined`，先定位原因再修。
5. 更新 README 里的日志接入说明，补上 `newLogger` 的用法、迁移前后的对照和常见错误。
6. 通读 `src/pages/` 下所有页面组件，找出还在手写字符串拼接日志的地方，列出清单后统一改成结构化日志，改完跑一遍构建和现有测试。
