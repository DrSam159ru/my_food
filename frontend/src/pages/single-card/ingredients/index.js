import React from "react";
import styles from "./styles.module.css";

/**
 * Ингредиенты в «глянцевой» журнальной карточке:
 * - тёмный фон с мягким бликом и тенью
 * - аккуратный заголовок и разделитель
 * - список сохраняет текущий формат: "Название — количество ед."
 */
const Ingredients = ({ ingredients }) => {
  if (!ingredients || !Array.isArray(ingredients) || ingredients.length === 0) {
    return null;
  }

  return (
    <section
      className={styles.ingredientsCard}
      role="region"
      aria-label="Ингредиенты рецепта"
    >
      <header className={styles.header}>
        <h3 className={styles.title}>Ингредиенты</h3>
        <div className={styles.decor} />
      </header>

      <ul className={styles.list}>
        {ingredients.map(({ name, amount, measurement_unit }) => (
          <li
            key={`${name}${amount}${measurement_unit}`}
            className={styles.item}
          >
            <span className={styles.itemName}>{name}</span>
            <span className={styles.dot} aria-hidden="true" />
            <span className={styles.itemAmount}>
              {amount} {measurement_unit}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
};

export default Ingredients;
