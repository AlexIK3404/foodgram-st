import { Card, Title, Pagination, CardList, Container, Main, CheckboxGroup } from '../../components'
import styles from './styles.module.css'
import { useRecipes } from '../../utils/index.js'
import { useEffect } from 'react'
import api from '../../api'
import { Helmet } from "react-helmet";

const HomePage = ({ updateOrders }) => {
  const {
    recipes,
    setRecipes,
    recipesCount,
    setRecipesCount,
    recipesPage,
    setRecipesPage,
    handleLike,
    handleAddToCart
  } = useRecipes()

  const getRecipes = ({ page = 1 }) => {
    api
      .getRecipes({ page })
      .then(res => {
        const { results, count } = res
        setRecipes(results)
        setRecipesCount(count)
      })
  }

  useEffect(_ => {
    getRecipes({ page: recipesPage })
  }, [recipesPage])


  return <Main>
    <Container>
      <Helmet>
        <title>Рецепты</title>
        <meta name="description" content="Фудграм - Рецепты" />
        <meta property="og:title" content="Рецепты" />
      </Helmet>
      <div className={styles.title}>
        <Title title='Рецепты' />
      </div>
      {recipes.length > 0 && <CardList>
        {recipes.map(card => <Card
          {...card}
          key={card.id}
          updateOrders={updateOrders}
          handleLike={handleLike}
          handleAddToCart={handleAddToCart}
        />)}
      </CardList>}
      <Pagination
        count={recipesCount}
        limit={6}
        page={recipesPage}
        onPageChange={page => setRecipesPage(page)}
      />
    </Container>
  </Main>
}

export default HomePage

