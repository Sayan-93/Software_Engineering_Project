import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models.models import Product, Category
from models import db

# Global cache (so we don't recompute every request)
product_df = None
similarity_matrix = None


def build_recommendations():
    global product_df, similarity_matrix

    products = Product.query.filter_by(is_active=True).all()

    data = []
    for p in products:
        category = db.session.get(Category, p.category_id)

        text = f"{p.name} {p.description or ''} {category.name if category else ''}"

        data.append({
            "id": p.id,
            "text": text
        })

    product_df = pd.DataFrame(data)

    if product_df.empty:
        similarity_matrix = None
        return

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(product_df["text"])

    similarity_matrix = cosine_similarity(tfidf_matrix)


def get_recommendations_for_product(product_id, top_n=2):
    global product_df, similarity_matrix

    if product_df is None or similarity_matrix is None:
        build_recommendations()

    if product_df is None or product_df.empty:
        return []

    try:
        idx = product_df[product_df["id"] == product_id].index[0]
    except IndexError:
        return []

    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Skip itself
    sim_scores = sim_scores[1:top_n+1]

    product_ids = [int(product_df.iloc[i[0]]["id"]) for i in sim_scores]

    if not product_ids:
        return []

    products = Product.query.filter(Product.id.in_(product_ids)).all()
    products_by_id = {p.id: p for p in products}

    # Keep the response order aligned with the similarity ranking.
    return [products_by_id[pid].to_dict() for pid in product_ids if pid in products_by_id]
