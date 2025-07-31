# TODO: Vault Project Roadmap

## Фаза 0: Финальная фиксация

- [x] Зафиксировано ТЗ (plugin/docs/tech_spec.md)
- [x] Зафиксирована архитектура (plugin/docs/architecture_vault.md)
- [ ] Создать `ARCHIVE/` для отложенных идей (мессенджер, OTP, др.)

---

## Фаза 1: Каркас проекта и утилиты

- [x] Структура src/ (core/, ui/, cloud/)
- [ ] Конфигурация Vite + Tailwind + manifest
- [ ] Папка public/ и context/
- [ ] Утилиты:

  - [ ] keyUtils.js (SHA256, PBKDF2, seed)
  - [ ] cryptoUtils.js (ChaCha20, HMAC)
  - [ ] timeUtils.js (блоки, timestamp)

---

## Фаза 2: CryptoEngine

- [ ] CryptoEngine класс

  - [ ] encryptFile()
  - [ ] decryptFile()
  - [ ] deriveKey(), generateKey()
  - [ ] verifyHMAC()

- [ ] Интеграция libsodium.js
- [ ] Подготовка wasm (опционально)

---

## Фаза 3: SafeSync

- [ ] Класс SafeSync:

  - [ ] TrackFile / UntrackFile
  - [ ] SyncFiles / ConflictResolution
  - [ ] WebSocket или polling (Google Drive API)

- [ ] GoogleDriveProvider (минимум)
- [ ] DropboxProvider, OneDriveProvider (заглушки)

---

## Фаза 4: UI

- [ ] EncryptionForm (реализация и связывание)
- [ ] Основная страница / layout
- [ ] Компоненты:

  - [ ] FileSelector, DropZone
  - [ ] ResultModal, ProgressIndicator

---

## Фаза 5: Генератор (вне плагина)

- [ ] Прототип генератора (телефон / десктоп)

  - [ ] Генерация seed (аудио, касание)
  - [ ] Экспорт seed через QR / BT

- [ ] Мини-приложение на JS / Flutter / Python

---

## Фаза 6: Premium-функции

- [ ] Гибридное шифрование (ChaCha20 + Kyber)
- [ ] Поддержка Dilithium-подписей
- [ ] Расширенная синхронизация (OneDrive, Dropbox)

---

## Фаза 7: Тестирование и аудит

- [ ] Юнит-тесты CryptoEngine
- [ ] Интеграционные тесты SafeSync + UI
- [ ] NIST/DIEHARDER тесты + OWASP ZAP

---

## Фаза 8: Сборка и публикация

- [ ] manifest.json и Chrome Store публикация
- [ ] Билд vite
- [ ] Инструкция по установке
- [ ] Лендинг / сайт

---

_Проект Vault: "Нарисуй. Подпиши. Защити."_
