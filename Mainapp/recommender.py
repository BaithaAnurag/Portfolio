import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from .models import Project, ProjectView

def recommend_projects(project_id, top_n=3):
    """Content-based recommendation using TF-IDF."""
    projects = Project.objects.all()
    if not projects.exists():
        return []

    # Build DataFrame
    data = pd.DataFrame(list(projects.values("id", "title", "description", "tags")))

    # Combine text fields
    data["content"] = data["title"].fillna("") + " " \
                      + data["description"].fillna("") + " " \
                      + data["tags"].fillna("")

    # Vectorize
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(data["content"])

    # Cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Index of the given project
    try:
        idx = data[data["id"] == project_id].index[0]
    except IndexError:
        return []

    # Similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Exclude itself, top N
    sim_scores = sim_scores[1:top_n+1]
    project_indices = [i[0] for i in sim_scores]

    return projects.filter(id__in=data.iloc[project_indices]["id"].values)


def collaborative_recommend(project_id, top_n=3):
    """Collaborative recommendation using ProjectView logs."""
    sessions = ProjectView.objects.filter(project_id=project_id).values_list("session_id", flat=True)
    other_views = ProjectView.objects.filter(session_id__in=sessions).exclude(project_id=project_id)

    counter = Counter(other_views.values_list("project_id", flat=True))
    most_common_ids = [pid for pid, _ in counter.most_common(top_n)]

    return Project.objects.filter(id__in=most_common_ids)


def hybrid_recommend(project_id, top_n=3):
    """Hybrid recommender: combine collaborative + content-based."""
    collab = collaborative_recommend(project_id, top_n)
    if collab.exists():
        return collab
    return recommend_projects(project_id, top_n)
