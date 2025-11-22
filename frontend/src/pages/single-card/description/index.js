import React from 'react';
import styles from './styles.module.css';

/**
 * Глянцевое описание рецепта:
 * - выравнивание по ширине
 * - переносы по слогам (hyphens)
 * - аккуратные абзацы и межстрочные интервалы
 * - дроп-кэп в первом абзаце
 * - адаптивная «журнальная» карточка
 */
const Description = ({ description }) => {
  if (!description) return null;

  // Нормализуем строку и разбиваем на абзацы по пустой строке / двойному переносy
  const paragraphs = String(description)
    .trim()
    .split(/\n{2,}|\r{2,}/)
    .map((p) => p.trim())
    .filter(Boolean);

  // Первый абзац — с красивой «буквицей»
  const renderWithDropcap = (text) => {
    if (!text) return null;
    const firstChar = text.charAt(0);
    const rest = text.slice(1);
    return (
      <p className={styles.paragraph}>
        <span className={styles.dropcap} aria-hidden="true">{firstChar}</span>
        {rest}
      </p>
    );
  };

  return (
    <section className={styles.description} role="article" aria-label="Описание рецепта">
      <header className={styles.header}>
        <h3 className={styles.title}>Описание</h3>
        <div className={styles.decor} />
      </header>

      <div className={styles.content}>
        {paragraphs.length > 0 && renderWithDropcap(paragraphs[0])}
        {paragraphs.slice(1).map((p, idx) => (
          <p key={idx} className={styles.paragraph}>{p}</p>
        ))}
      </div>
    </section>
  );
};

export default Description;
