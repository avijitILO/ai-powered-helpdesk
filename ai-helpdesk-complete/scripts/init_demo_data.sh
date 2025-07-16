#!/bin/bash

echo "📊 Initializing demo data..."

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Initialize Zammad demo data
echo "🎫 Setting up Zammad demo data..."
docker-compose exec -T zammad-railsserver rails r "
# Create demo groups
groups = [
  {name: 'IT Support', note: 'Information Technology support team'},
  {name: 'HR Support', note: 'Human Resources support team'},
  {name: 'Finance', note: 'Finance and accounting team'},
  {name: 'Facilities', note: 'Facilities management team'}
]

groups.each do |group_data|
  group = Group.find_by(name: group_data[:name]) || Group.create!(group_data)
  puts \"Created group: #{group.name}\"
end

# Create demo users
users = [
  {firstname: 'John', lastname: 'Doe', email: 'john.doe@company.com', login: 'john.doe'},
  {firstname: 'Jane', lastname: 'Smith', email: 'jane.smith@company.com', login: 'jane.smith'},
  {firstname: 'Bob', lastname: 'Johnson', email: 'bob.johnson@company.com', login: 'bob.johnson'}
]

users.each do |user_data|
  user = User.find_by(email: user_data[:email]) || User.create!(user_data.merge(
    password: 'password123',
    verified: true,
    active: true
  ))
  puts \"Created user: #{user.email}\"
end

puts 'Demo data initialization completed!'
"

# Initialize BookStack demo data
echo "📚 Setting up BookStack demo data..."

# Wait for BookStack to be ready
sleep 15

# Create demo content via API (simplified)
echo "📝 BookStack demo content will be available after first login"

echo "✅ Demo data initialization completed!"
echo ""
echo "📋 Demo Accounts:"
echo "  Zammad: admin@example.com / test"
echo "  BookStack: admin@admin.com / password"
echo "  Demo Users: john.doe@company.com / password123"