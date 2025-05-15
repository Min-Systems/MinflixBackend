import pytest
from app.main import lifespan


@pytest.mark.asyncio
async def test_lifespan_dynamic_mode(mock_app, dynamic_mode_config, mock_db_session):
    """Test lifespan function in Dynamic mode."""
    # Use the async context manager
    async with lifespan(mock_app):
        pass  # Inside the lifespan context
    
    # Verify the expected functions were called
    dynamic_mode_config['drop_all_tables'].assert_called_once()
    dynamic_mode_config['create_db_and_tables'].assert_called_once()
    dynamic_mode_config['add_films'].assert_called_once_with(mock_db_session)


@pytest.mark.asyncio
async def test_lifespan_production_mode(mock_app, production_mode_config, mock_db_session):
    """Test lifespan function in Production mode."""
    # Use the async context manager
    async with lifespan(mock_app):
        pass  # Inside the lifespan context
    
    # Verify the expected functions were called
    production_mode_config['drop_all_tables'].assert_not_called()  # Should not be called in Production mode
    production_mode_config['create_db_and_tables'].assert_called_once()
    production_mode_config['add_films'].assert_called_once_with(mock_db_session)


@pytest.mark.asyncio
async def test_lifespan_example_mode(mock_app, example_mode_config, mock_db_session):
    """Test lifespan function in Example mode."""
    # Use the async context manager
    async with lifespan(mock_app):
        pass  # Inside the lifespan context
    
    # Verify the expected functions were called
    example_mode_config['drop_all_tables'].assert_called_once()
    example_mode_config['create_db_and_tables'].assert_called_once()
    example_mode_config['create_example_data'].assert_called_once_with(mock_db_session)
    example_mode_config['add_films'].assert_called_once_with(mock_db_session)


@pytest.mark.asyncio
async def test_lifespan_films_already_present(mock_app, dynamic_mode_config, films_present_config):
    """Test lifespan function when films are already in the database."""
    # Use the async context manager
    async with lifespan(mock_app):
        pass  # Inside the lifespan context
    
    # Verify the expected functions were called
    dynamic_mode_config['drop_all_tables'].assert_called_once()
    dynamic_mode_config['create_db_and_tables'].assert_called_once()
    dynamic_mode_config['add_films'].assert_not_called()  # Should not be called when films are present