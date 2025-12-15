# CohortAI - Smart Recommendation System

## Overview

CohortAI is an e-commerce platform with a smart recommendation system that learns from user behavior to provide personalized product suggestions. The system uses behavioral tracking and collaborative filtering instead of traditional machine learning clustering.

## Architecture

### Key Components

1. **User Interaction Tracking**
   - Tracks product views, cart additions, and purchases
   - Different weights for different actions (view: 0.1, cart: 0.5, purchase: 1.0)
   - Automatic tracking via middleware and signals

2. **Product Similarity Engine**
   - Uses TF-IDF vectorization for text similarity
   - Compares products based on name, description, category, and tags
   - Pre-computed similarity matrix for performance

3. **Recommendation Algorithm**
   - Content-based filtering (70% weight)
   - Collaborative filtering (30% weight)
   - Fallback to popular products

4. **Dynamic Recommendations**
   - Real-time updates based on user behavior
   - No manual segment assignments required
   - Adapts to changing preferences

## How It Works

### Step 1: User Interaction Tracking

When users interact with the site:
- **View a product**: Automatically tracked via middleware
- **Add to cart**: Tracked via signals
- **Purchase**: Tracked via order creation

All interactions are stored in `UserProductInteraction` table with weights indicating importance.

### Step 2: Product Similarity Calculation

Products are compared using:
- Text similarity (name and description)
- Category matching
- Tag overlap
- Calculated using TF-IDF and cosine similarity

Similarity scores are pre-computed and stored in `ProductSimilarity` table.

### Step 3: Generating Recommendations

For each user, the system:

1. **Content-Based Recommendations**:
   - Looks at user's recent interactions
   - Finds similar products using similarity matrix
   - Recommends products with highest similarity scores

2. **Collaborative Filtering**:
   - Finds users with similar interaction patterns
   - Recommends products those users liked
   - Uses "users who liked X also liked Y" logic

3. **Hybrid Approach**:
   - Combines both methods
   - Deduplicates results
   - Falls back to popular products if no data

## Installation and Setup

### Prerequisites

- Python 3.8+
- Django 6.0+
- Virtual environment

### Setup Steps

1. **Clone and Setup Environment**
   ```bash
   git clone <repository-url>
   cd CohortAI
   python -m venv env
   env\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Initialize Product Similarities**
   ```bash
   python manage.py update_similarities
   ```

4. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run Server**
   ```bash
   python manage.py runserver
   ```

## Using the System

### For Users

1. **Register/Login**: Create an account or log in
2. **Browse Products**: Views are automatically tracked
3. **Add to Cart**: Interactions are recorded
4. **See Recommendations**: Personalized products appear on homepage and product pages

### For Admins

1. **Access Admin Panel**: `/admin/`
2. **Manage Products**: Add products with descriptions and tags
3. **View Interactions**: Monitor user engagement
4. **Update Similarities**: Run `python manage.py update_similarities` after adding products

## Database Models

### Core Models

- **Product**: Products with name, description, price, category, and tags
- **ProductTag**: Tags for categorizing products
- **UserProductInteraction**: Tracks user interactions with products
- **ProductSimilarity**: Pre-computed similarity scores between products

### Key Relationships

- Products can have multiple tags
- Users can have multiple interactions with products
- Products have similarity scores with other products

## API Endpoints

### Views

- `/` - Homepage with personalized recommendations
- `/product/<slug>/` - Product detail page with recommendations
- `/cart/` - Shopping cart
- `/profile/` - User profile (original clustering interface available at `/customer-segmentation/`)

### Admin

- `/admin/` - Django admin panel
- Manage products, tags, and view interaction data

## Recommendation Engine Details

### Content-Based Filtering

Uses TF-IDF vectorization to convert product text into numerical vectors:
- Analyzes product names and descriptions
- Considers category and tags
- Calculates cosine similarity between products

### Collaborative Filtering

Finds patterns in user behavior:
- Identifies users with similar interaction histories
- Recommends products liked by similar users
- Improves as more users interact with the system

### Weight System

Different actions have different importance:
- View: 0.1 (light signal)
- Add to cart: 0.5 (medium signal)
- Purchase: 1.0 (strong signal)

## Testing the System

### Test Users

The system includes test users for demonstration:
- `fashion_lover` (password: testpass123)
- `tech_enthusiast` (password: testpass123)
- `home_maker` (password: testpass123)

### Demo Script

Run the demo to see recommendations in action:
```bash
python manage.py shell < demo_interactions.py
```

### Manual Testing

1. Register a new user
2. Browse different product categories
3. Add items to cart
4. Observe changing recommendations on homepage

## Differences from Original System

### Old System (Clustering)
- Used K-Means clustering on age, income, spending score
- Fixed customer segments
- Manual product-to-segment assignment
- Rigid and static recommendations

### New System (Behavioral)
- Tracks actual user behavior
- Dynamic recommendations
- No manual assignments needed
- Adapts to individual preferences

## Maintenance

### Regular Tasks

1. **Update Similarities**: Run after adding new products
   ```bash
   python manage.py update_similarities
   ```

2. **Monitor Interactions**: Check admin panel for user engagement
3. **Add Product Tags**: Improve recommendations with better tagging

### Performance Considerations

- Similarity matrix is pre-computed for fast recommendations
- Interactions are tracked asynchronously
- Recommendations cached per user session

## Troubleshooting

### Common Issues

1. **No Recommendations Showing**
   - Ensure product similarities are updated
   - Check that user has interaction history
   - Verify products have tags and descriptions

2. **Slow Performance**
   - Run update_similarities command
   - Check database indexes
   - Monitor interaction table size

3. **Poor Recommendations**
   - Add more descriptive product information
   - Improve product tagging
   - Ensure users have sufficient interaction history

## Future Enhancements

Potential improvements:
- Real-time similarity updates
- More sophisticated collaborative filtering
- A/B testing framework
- Advanced analytics dashboard
- Email recommendation campaigns

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

This project is for educational purposes to demonstrate recommendation systems.