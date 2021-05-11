const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const OptimizeCssAssetsPlugin = require("optimize-css-assets-webpack-plugin");
const path = require('path');
const setPublicPath = require('@microsoft/set-webpack-public-path-plugin');
const webpack = require('webpack');

// Only embed assets under 10 KB
const embedLimit = 10 * 1024;

const devServerPort = 8080;

const pathRoot = 'frontend';
const pathDist = `${pathRoot}/dist`;
const pathDistGov = path.resolve(__dirname, pathDist, 'govuk');


/*
** Rules which change depending on mode
*/

// Image optimisation rule
const moduleRuleOptimiseImages = {
  test: /\.(gif|png|jpe?g|svg)$/i,
  loader: 'image-webpack-loader',
  options: {
    // Apply the loader before url-loader and svg-url-loader
    enforce: 'pre',
    // Disabled in dev, enable in production
    disable: true,
  },
};

// Style building rule
const moduleRuleScss = {
  test: /\.scss$/,
  use: [
    // MiniCssExtractPlugin doesn't support HMR, so will replace style-loader
    // in production
    'style-loader',
    'css-loader',
    {
      loader: 'resolve-url-loader',
      options: {
        'sourceMap': true,
      },
    },
    {
      loader: 'sass-loader',
      options: {
        sassOptions: {
          includePaths: ['./node_modules'],
          sourceMap: true,
          sourceMapContents: false
        },
      },
    },
  ],
};


/*
** Main config
*/
const config = {
  entry: {
    // 'index': [`./${pathRoot}/src/index.js`, `./${pathRoot}/src/index.scss`],
    'index': `./${pathRoot}/src/index.js`,
    'style': `./${pathRoot}/src/index.scss`
  },
  output: {
    path: path.resolve(__dirname, pathDist),
    publicPath: `/${pathDist}/`,
    filename: '[name].js',
    library: "NSCR"
  },

  // Enable sourcemaps for debugging webpack's output.
  devtool: 'source-map',
  devServer: {
    contentBase: path.resolve(__dirname, pathDist),
    contentBasePublicPath: '/static/',
    publicPath: '/static/',
    hot: true,
    disableHostCheck: true,
    port: devServerPort,
    headers: {
      'Access-Control-Allow-Origin': '*'
    },
    writeToDisk: (filePath) => {
      // Write to disk if path starts as the copied GOV.UK assets
      return filePath.startsWith(pathDistGov);
    },
  },

  resolve: {
    extensions: ['.js', '.json']
  },

  plugins: [
    new CleanWebpackPlugin({
      // Remove built js and css from the dist folder before building
      cleanOnceBeforeBuildPatterns: ['**/*', '!.gitkeep'],
    }),
    new MiniCssExtractPlugin({
      // Options similar to the same options in webpackOptions.output
      // both options are optional
      filename: '[name].css',
    }),
    new CopyPlugin(
      [
        // Copy GOV.UK assets into the dist path without modifying
        {
          context: path.resolve(__dirname, 'node_modules/govuk-frontend/govuk/assets'),
          from: '**/*',
          to: pathDistGov,
       },
      ],
    ),
  ],

  module: {
    rules: [
      // All output '.js' files will have any sourcemaps re-processed by 'source-map-loader'.
      {
        test: /\.js$/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },

      // Optimise images
      moduleRuleOptimiseImages,

      // Embed small images and fonts
      {
        test: /\.(png|jpg|gif|eot|ttf|woff|woff2)$/,
        loader: 'url-loader',
        options: {
          limit: embedLimit,
        },
      },
      {
        test: /\.svg$/,
        loader: 'svg-url-loader',
        options: {
          limit: embedLimit,
          noquotes: true,
        }
      },

      // SCSS
      moduleRuleScss,
    ],
  },
};


module.exports = (env, argv) => {
  if (argv.mode === 'production') {
    console.log(`Running in production mode:
* optimising images
* extracting and minifying CSS
    `);

    // Switch from style-loader to generate separate css files
    moduleRuleScss.use[0] = MiniCssExtractPlugin.loader;

    // Activate image optimisation
    moduleRuleOptimiseImages.options.disable = false;

    // Optimise CSS assets
    config.plugins.push(new OptimizeCssAssetsPlugin());

  } else if (process.argv[1].indexOf('webpack-dev-server') !== -1) {
    console.log('Running in development mode with HMR');

    // Add HMR and change the public path to pick up the correct hostname
    config.plugins.push(
      new webpack.HotModuleReplacementPlugin(),
      new setPublicPath.SetPublicPathPlugin({
        scriptName: {
          name: '[name]\.js',
          isTokenized: true,
        },
      }),
    );

  } else {
    console.log('Running in development mode');

    // Add HMR
    config.plugins.push(
      new webpack.HotModuleReplacementPlugin(),
    )
  }
  return config;
}
