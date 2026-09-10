#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { PantryPilotStack } from '../lib/pantry-pilot-stack';

const app = new cdk.App();

// Instantiate our custom PantryPilotStack
new PantryPilotStack(app, 'PantryPilotStack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION 
  },
});