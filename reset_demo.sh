#!/bin/bash

# ==========================================
# PantryPilot Demo Reset Script
# ==========================================

TABLE_NAME="PantryPilotStack-PantryTable62697913-GHGB6AZY5FX3"
BUCKET_NAME="pantry-pilot-assets-741714103560"

echo "🧹 Starting PantryPilot Demo Reset..."
echo "---------------------------------------------------"

# 1. Delete all items in DynamoDB
echo "1️⃣  Clearing DynamoDB Table: $TABLE_NAME"
aws dynamodb scan --table-name "$TABLE_NAME" --query "Items[*].[pk.S, sk.S]" --output text | while IFS=$'\t' read -r pk sk; do
  if [ -n "$pk" ] && [ -n "$sk" ]; then
    aws dynamodb delete-item --table-name "$TABLE_NAME" --key "{\"pk\": {\"S\": \"$pk\"}, \"sk\": {\"S\": \"$sk\"}}" > /dev/null
  fi
done
echo "   ✅ DynamoDB table cleared."

# 2. Delete all items in S3 processed_messages/
echo "2️⃣  Clearing S3 folder: s3://$BUCKET_NAME/processed_messages/"
aws s3 rm "s3://$BUCKET_NAME/processed_messages/" --recursive
echo "   ✅ processed_messages/ folder cleared."

# 3. Delete all items in S3 receipts/
echo "3️⃣  Clearing S3 folder: s3://$BUCKET_NAME/receipts/"
aws s3 rm "s3://$BUCKET_NAME/receipts/" --recursive
echo "   ✅ receipts/ folder cleared."

# 4. Delete specific voice transcription files in S3 received_messages/
echo "4️⃣  Deleting specific voice transcription files from received_messages/..."
aws s3 rm "s3://$BUCKET_NAME/received_messages/+15551233_voice_bill.txt"
echo "   ✅ Specific voice files deleted."

# 5. ✅ RECREATE ALL FOLDERS IMMEDIATELY (Using touch)
echo "5️⃣  Recreating S3 folders so they remain visible..."
touch .keep
aws s3 cp .keep "s3://$BUCKET_NAME/received_voice/.keep"
aws s3 cp .keep "s3://$BUCKET_NAME/received_messages/.keep"
aws s3 cp .keep "s3://$BUCKET_NAME/processed_messages/.keep"
aws s3 cp .keep "s3://$BUCKET_NAME/receipts/.keep"
rm .keep
echo "   ✅ All folders recreated and visible in S3 Console."

echo "---------------------------------------------------"
echo "🎉 Reset Complete! Your demo environment is fresh."
echo "💡 Next Step: Open the Dashboard and click '🔄 Scan Inbox'."