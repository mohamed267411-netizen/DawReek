CREATE DATABASE UserSystem;
GO

CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1), 
    FullName NVARCHAR(100) NOT NULL,    
    Email NVARCHAR(150) NOT NULL UNIQUE,  
    PasswordHash NVARCHAR(MAX) NOT NULL,  
    FavoriteTeam NVARCHAR(50)            
);
GO
